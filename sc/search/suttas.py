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

logger = logging.getLogger(__name__)

class SuttaIndexer(ElasticIndexer):
    doc_type = 'sutta'

    def extract_fields(self, sutta):
        boost = log(3 + sum(2 - p.partial for p in sutta.parallels), 10)
        return {
            "uid": sutta.uid,
            "volpage": [sutta.volpage] + ([sutta.alt_volpage_info]
                                            if sutta.alt_volpage_info else []),
            "division": sutta.subdivision.uid,
            "lang": sutta.lang.uid,
            "name": sutta.name,
            "boost": boost
        }
    
    def yield_suttas(self, size):
        chunk = []
        chunk_size = 0
        for _, sutta in sorted(sc.scimm.imm().suttas.items()):
            action = {
                '_id': sutta.uid
            }
            action.update(self.extract_fields(sutta))
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
        state = sorted(f.stat().st_mtime_ns for f in sc.table_dir.glob('*.csv'))
        return state
        
    def is_updated_needed(self):
        # Always completely rebuild index if data changes
        if not self.index_exists():
            return True
        if not self.alias_exists():
            return True
        return False
    
    def update_data(self, force=False):
        index_name = self.index_name
        self.process_chunks(self.yield_suttas(size=500000))

def periodic_update(i):
    if not sc.search.is_available():
        logger.error('Elasticsearch Not Available')
        return
    indexer = SuttaIndexer('suttas')
    indexer.update()
            
