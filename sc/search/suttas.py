import json
import time
import regex
import hashlib
import logging
import lxml.html
from math import log
from copy import deepcopy
from collections import defaultdict
from elasticsearch.helpers import bulk, scan
import sc
from sc import textfunctions
from sc.search import load_index_config
from sc.util import recursive_merge, numericsortkey, grouper, unique

logger = logging.getLogger(__name__)

class SuttaIndexer(sc.search.BaseIndexer):
    index_alias = 'suttas'
    index_prefix = 'suttas_'
    
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

    def update(self, force=False):
        """ Suttas are indexed in indexes named:
        
        suttas_299a0be4

        Where the second part is a md5 digest of the index config
        and the mtimes of the csv files.

        That index is aliased to "suttas".

        When the config changes, or when the csv files change,
        a new md5 digest is generated, a new index is generated,
        and the alias updated.

        """
        self.register_index(self.index_alias)
        index_config = load_index_config('sutta')
        md5 = hashlib.md5()
        state = sorted(f.stat().st_mtime_ns for f in sc.table_dir.glob('*.csv'))
        state.append(index_config)
        md5.update(json.dumps(state, sort_keys=True).encode(encoding='ascii'))
        self.state = state

        state_md5 = md5.hexdigest()[:10]

        indexes_to_alias = self.es.indices.get_aliases(self.index_alias)
        for index in indexes_to_alias:
            if index == self.index_prefix + state_md5:
                return

        index_name = self.index_prefix + state_md5
        if force:
            try:
                self.es.indices.delete(index_name)
            except:
                pass
        
        if not self.es.indices.exists(index_name):
            logger.info('Creating index "{}"'.format(index_name))
            self.es.indices.create(index_name, index_config)

        for chunk in self.yield_suttas(size=500000):
            if not chunk:
                continue
            
            try:
                res = bulk(self.es, index=index_name, doc_type="sutta", actions=(t for t in chunk if t is not None))
            except:
                raise
        aliases_actions = []
        for index in indexes_to_alias:
            aliases_actions.append({"remove": {"index": index, "alias": self.index_alias}})
        aliases_actions.append({"add": {"index": index_name, "alias": self.index_alias}})
        self.es.indices.update_aliases({"actions": aliases_actions})
        for index in indexes_to_alias:
            self.es.indices.delete(index)

indexer = SuttaIndexer()

def search(query, highlight=True, **kwargs):
    body = {
        "query": {
            "query_string": {
                "default_field": "content",
                "fields": ["content", "content.folded", "content.stemmed"],
                "minimum_should_match": "60%",
                "query": query
                }
            }
        }
    if highlight:
        body["highlight"] = {
            "pre_tags": ['<strong class="highlight">'],
            "post_tags": ['</strong>'],
            "order": "score",
            "fields": {
                "content" : {
                    "matched_fields": ["content", "content.folded", "content.stemmed"],
                    "type": "fvh",
                    "fragment_size": 100,
                    "number_of_fragments": 3
                    }
                }
            }
    return es.search(body=body, **kwargs)

def periodic_update(i):
    try:
        indexer.update()
    except Exception as e:
        logger.error('Elasticsearch failure: {!s}'.format(e))
            
