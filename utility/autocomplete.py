from elasticsearch import Elasticsearch
from elasticsearch.helpers import scan, bulk
import itertools
from collections import defaultdict
es = Elasticsearch()
if es.indices.exists('autocomplete'):
    es.indices.delete('autocomplete')

body = {
    "settings": {
        "analysis": {
            "filter": {
                "autocomplete_filter": {
                    "type": "edge_ngram",
                    "min_gram": 3,
                    "max_gram": 20
                }
            },
            "analyzer": {
                "autocomplete_analyzer": {
                    "type": "custom",
                    "tokenizer": "standard",
                    "filter": [
                        "lowercase",
                        "autocomplete_filter"
                    ]
                }
            }
        }
    },
      "mappings": {
         "thingy": {
            "properties": {
               "lang": {
                  "type": "string"
               },
               "title": {
                  "type": "string",
                    "index_analyzer": "autocomplete_analyzer",
                    "search_analyzer": "standard"
               },
               "boost": {
                "type": "float"
                }
            }
         }
      }
}

r = es.indices.create('autocomplete', body=body)
print(r)

# Extract text titles
text_titles = [{k:v[0] for k,v in hit['fields'].items()} for hit in scan(es,
    index='_all',
    doc_type="text",
    fields=["uid", "lang", "boost", "heading.title"],
    query=None,
    size=500)]

# Extract sutta titles
sutta_titles = [{k:v[0] for k,v in hit['fields'].items()} for hit in scan(es,
    index='suttas',
    doc_type='sutta',
    fields=['uid', 'lang', "boost", 'name'],
    size=500)]

entries = defaultdict(list)
for entry in text_titles:
    entries[(entry['heading.title'], entry['lang'])].append(entry['boost'])
#entries.update((d['heading.title'], d['lang']) for d in text_titles)
for entry in sutta_titles:
    entries[(entry['name'], entry['lang'])].append(entry['boost'])
    

def as_string():
    import json
    return json.dumps([(k[0].replace('\xad', ''), k[1], max(v)) for k,v in entries.items()])

actions = ({"title": k[0].replace('\xad', ''),
            "lang": k[1],
            "boost": 0.5 * (max(v) + sum(v) / len(v))} for k,v in entries.items())

loaded = 0
while True:
    chunk = list(itertools.islice(actions, 500))
    if not chunk:
        break
    loaded += len(chunk)
    print('Loaded {}'.format(loaded), end='\r')
    res = bulk(es,
                index='autocomplete',
                doc_type='thingy',
                actions=chunk)

def go(query, **params):
    body = {
        "query": {
            "function_score": {
                "query": {
                    "match": {
                        "title": query
                    }
                },
                "functions": [{
                    "field_value_factor": {
                        "field": "boost"
                        }
                }],
                "score_mode": "multiply"
            }
        }
    }
    body.update(params)
    return es.search('autocomplete', 'thingy', body=body)
