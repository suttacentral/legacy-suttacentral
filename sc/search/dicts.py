import time
import regex

import logging
logger = logging.getLogger(__name__)

import elasticsearch

es = elasticsearch.Elasticsearch()

def get_entry(lang, term):
    out = {}
    try:
        resp = es.get(index=lang, doc_type='definition', id=term)
    except:
        return None
    source = resp['_source']

    out['entry'] = source
    out['entry']['entries'].sort(key=lambda d: d['priority'])

    number = source['number']

    resp = es.search('en', doc_type='definition', _source=['term', 'gloss'], body={
      "query":{
         "constant_score": {
           "filter": {
             "range": {
               "number": {
                 "gte": number - 10,
                 "lte": number + 10
               }
             }
           }
         }
      }
    })

    out['near'] = [d['_source'] for d in resp['hits']['hits']]

    resp = es.search('en', doc_type='definition', _source=['term', 'gloss'], body={
        "query": {
            "fuzzy_like_this": {
                "fields": ["term", "term.folded"],
                "like_text": term
            }
        }
    })

    out['fuzzy'] = [d['_source'] for d in resp['hits']['hits']]
    return out
    
