import json
import time
import regex
import logging
import lxml.html
from math import log
from copy import deepcopy
from collections import defaultdict
import sc
from sc import textfunctions
from sc.search.indexer import ElasticIndexer

logger = logging.getLogger('search.suttas')

sutta_dump_file = sc.db_dir / 'suttas.json'

class SuttaDumper:
    def __init__(self):
        self.volpage_mapping = self.calculate_sutta_volpages()
        self.last_imm_timestamp = None
    
    def calculate_sutta_volpages(self):
        rex = regex.compile(r'^(?<vol>\D+)(?<page>\d+)$')
        mapping = {}
        prev_sutta = None
        suttas = [s for s in sc.scimm.imm().suttas.values() if '-' not in s.uid]
        
        for sutta in suttas:
            if prev_sutta:
                # Calculate the volpage range for the previous sutta
                start = rex.match(prev_sutta.volpage)
                end = rex.match(sutta.volpage)
                if start and end and start['vol'] == end['vol']:
                    pages = []
                    for i in range(int(start['page']) + 1, int(end['page'])):
                        pages.append('{}{}'.format(start['vol'], i))
                    if pages:
                        mapping[prev_sutta.uid] = pages
            prev_sutta = sutta
        return mapping
    
    def extract_fields(self, sutta):
        boost = log(3 + sum(2 - p.partial for p in sutta.parallels), 10)
        try:
            return {
                "uid": sutta.uid,
                "volpage": [sutta.volpage] + ([sutta.alt_volpage_info]
                                                if sutta.alt_volpage_info else []),
                "volpage_extra": self.volpage_mapping.get(sutta.uid) or [sutta.volpage],
                "division": sutta.subdivision.division.uid,
                "subdivision": sutta.subdivision.uid,
                "lang": sutta.lang.uid,
                "name": sutta.name,
                "ordering": '{:04}.{:04}.{:04}'.format(
                             sutta.subdivision.division.menu_seq,
                             sutta.subdivision.order,
                             sutta.number),
                "boost": boost
            }
        except Exception as e:
            logger.exception('')
            return None
    
    def dump_suttas(self):
        imm = sc.scimm.imm()
        
        if imm.timestamp != self.last_imm_timestamp:
            self.last_imm_timestamp = imm.timestamp                
            
            out = sorted(filter(None, (self.extract_fields(sutta) for sutta in imm.suttas.values())), key=lambda s: s['ordering'])
            
            with sutta_dump_file.open('w') as f:
                json.dump(out, f, sort_keys=True)

class SuttaIndexer(ElasticIndexer):
    doc_type = 'sutta'
    version = 4
    
    def load_suttas(self):
        try:
            with sutta_dump_file.open('r') as f:
                return json.load(f)
        except FileNotFoundError:
            return []
    
    def yield_suttas(self, size):
        chunk = []
        chunk_size = 0
        suttas = self.load_suttas()
        
        for sutta in suttas:
            action = {
                '_id': sutta['uid']
            }
            action.update(sutta)
            chunk.append(action)
            chunk_size += len(str(action).encode(encoding='utf8'))
            if chunk_size > size:
                yield chunk
                chunk = []
                chunk_size = 0
        if chunk:
            yield chunk
        raise StopIteration

    def get_extra_state(self):
        try:
            with open(sutta_dump_file, 'rb') as f:
                return hashlib.md5(f.read()).hexdigest()
        except FileNotFoundError:
            return None
        
    def is_updated_needed(self):
        # Always completely rebuild index if data changes
        if not self.index_exists():
            return True
        if not self.alias_exists():
            return True
        return False
    
    def update_data(self, force=False):
        self.process_chunks(self.yield_suttas(size=500000))

def update(_cache={}):
    if 'dumper' not in _cache:
        _cache['dumper'] = SuttaDumper()
    
    if 'indexer' not in _cache:
        _cache['indexer'] = SuttaIndexer('suttas')
    
    dumper = _cache['dumper']
    indexer = _cache['indexer']
    dumper.dump_suttas()
    indexer.update()

def filter_search(query):
    if 'acronym' in query:
        query['uid'] = regex.sub(r'\s+', '', query['acronym']).lower()
        del query['acronym']
    mode = query.pop('mode')
    
    queries = []
    for key, value in query.items():
        if not value:
            continue
        queries.append({
            mode: {
                key: {
                 "value": value
                }
            }
        })
    if len(queries) == 0:
        return None
    
    body = {
        "query": {
            "bool": {
                "should": queries
            }
        }
    }
    
    return sc.search.es.search('suttas', body=body)
