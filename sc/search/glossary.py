import time
import json
import regex
import logging
import unicodedata
import sc
import sc.tools.html
import sc.textfunctions
from elasticsearch.helpers import bulk
from sc.search.indexer import ElasticIndexer
from collections import defaultdict
es = sc.search.es

logger = logging.getLogger(__name__)

def normalize(term):
    term = term.lower()
    term = unicodedata.normalize('NFC', term)
    term = term.replace('\xad', '').replace('ṁ', 'ṃ').replace('ṃg', 'ṅg').replace('ṃk', 'ṅk')
    return term

def load():
 try:
    file = sc.data_dir / 'dicts' / 'en' / 'bb_glossary.json'
    with file.open() as f:
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
    
    # Clear Entries if Needed:
    if es.indices.exists('pi2en-glossary'):
        query = {
            "query": {
                "term": {
                    "source": "bb_glossary"
                    }
                }
            }
        es.delete_by_query('pi2en-glossary', 'entry', query)
    
    # Load Entries
    bulk(client=es,
         actions=entries,
         index='pi2en-glossary',
         doc_type='entry')
    
    return entries
 except:
     globals().update(locals())
     raise 
                
            
        
        
    

