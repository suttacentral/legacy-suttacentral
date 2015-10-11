import json
import logging

import sc.search
from elasticsearch.helpers import scan, streaming_bulk

logger = logging.getLogger(__name__)

es = sc.search.es



def dump(index):
    if not sc.search.is_available():
        logger.error('Elasticsearch not available, unable to proceed')
        return
    r = scan(es, index=index)
    return list(r)

def load(entries, index):
    if not sc.search.is_available():
        logger.error('Elasticsearch not available, unable to proceed')
        return
    r = streaming_bulk(es, index=index, actions=entries)
    return list(r)


lookup_indexes = ('pali-lookup', 'pi2en-glossary')

def dump_lookup_data(file):
    data = {index: dump(index) for index in lookup_indexes}
    with open(str(file), 'w', encoding='utf8') as f:
        json.dump(data, f)
    
def load_lookup_data(file):
    with open(str(file), 'r', encoding='utf8') as f:
        data = json.load(f)
    for index, entries in data.items():
        load(entries, index)
    
