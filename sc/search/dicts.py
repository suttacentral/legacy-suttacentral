import time
import regex

import logging
logger = logging.getLogger(__name__)

import elasticsearch

es = elasticsearch.Elasticsearch()

def get_entry(term, lang='en'):
    out = {}
    try:
        resp = es.get(index=lang, doc_type='definition', id=term)
    except:
        return None
    source = resp['_source']
    source['entries'].sort(key=lambda d: d['priority'])
    return source

def get_nearby_terms(number, lang='en'):
    resp = es.search(index=lang, doc_type='definition', _source=['term', 'gloss'], body={
      "query":{
         "constant_score": {
           "filter": {
             "range": {
               "number": {
                 "gte": number - 5,
                 "lte": number + 5
               }
             }
           }
         }
      }
    }, size=12)
    return [d['_source'] for d in resp['hits']['hits']]

def get_fuzzy_terms(term, lang='en'):
    resp = es.search(index=lang, doc_type='definition', _source=['term', 'gloss'], body={
        "query": {
            "fuzzy_like_this": {
                "fields": ["term", "term.folded"],
                "like_text": term
            }
        }
    })
    return [d['_source'] for d in resp['hits']['hits'] if d['_source']['term'] != term]
    
