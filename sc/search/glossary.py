import time
import json
import regex
import logging
import unicodedata
import sc
import sc.tools.html
import sc.textfunctions
import elasticsearch.exceptions
from elasticsearch.helpers import bulk
from sc.search.indexer import ElasticIndexer
from collections import defaultdict
es = sc.search.es

logger = logging.getLogger(__name__)

INDEX_NAME = 'pi2en-glossary'
FILE = sc.data_dir / 'dicts' / 'en' / 'bb_glossary.json'

def normalize(term):
    term = term.lower()
    term = unicodedata.normalize('NFC', term)
    term = term.replace('\xad', '').replace('ṁ', 'ṃ').replace('ṃg', 'ṅg').replace('ṃk', 'ṅk')
    return term

def periodic_update(i):
    try:
        result = es.get(INDEX_NAME, 'mtime', 'mtime')
        stored_mtime = result['_source']['mtime']
    except (elasticsearch.exceptions.NotFoundError, KeyError):
        stored_mtime = None
    
    file_mtime = FILE.stat().st_mtime_ns
    if str(file_mtime) == str(stored_mtime):
        return
    else:
        load()
        es.index(INDEX_NAME, 'mtime', {'mtime': file_mtime}, 'mtime')

def load():
 try:
    with FILE.open() as f:
        data = json.load(f)
    seen = defaultdict(int)
    for pali, gloss, context in data:
        key = (pali, context)
        seen[key] += 1
    
    entries = []
    counter = defaultdict(int)
    for pali, gloss, context in data:
        key = (pali, context)
        if seen[key] > 1:
            if not context:
                counter[key] += 1
                context = str(counter[key])
        entries.append({
            "_source": {
                "term": pali,
                "normalized": normalize(pali),
                "gloss": gloss,
                "context": context,
                "comment": "",
                "source": "bb_glossary"
            },
            "_id": pali if not context else '{}-{}'.format(pali, context)
        })
    
    mapping = {}
    
    # Clear Entries if Needed:
    if es.indices.exists('pi2en-glossary'):
        query = {
            "query": {
                "term": {
                    "source": "bb_glossary"
                    }
                }
            }
        request = es.search('pi2en-glossary', 'entry', body=query, scroll='1m')
        while request['hits']['hits']:
            for hit in request['hits']['hits']:
                es.delete(index='pi2en-glossary', doc_type='entry', id=hit['_id'])
            request = es.scroll(request['_scroll_id'], scroll='1m')
    
    # Load Entries
    bulk(client=es,
         actions=entries,
         index='pi2en-glossary',
         doc_type='entry')
    
    return entries
 except:
     globals().update(locals())
     raise 
                
            
        
        
    

