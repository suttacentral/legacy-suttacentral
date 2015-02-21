from collections import defaultdict

from elasticsearch import Elasticsearch
from elasticsearch.helpers import scan

import sc.search

from sc.search.indexer import ElasticIndexer

es = Elasticsearch()
if es.indices.exists('autocomplete'):
    es.indices.delete('autocomplete')

class AutocompleteIndexer(ElasticIndexer):
    doc_type = 'autocomplete'

    def load_index_config(self, config_name):
        # Altough get_index_config normally loads a file
        # here we just define the index settings and mapping inline
        # as it is so very different and vastly simpler than the
        # the other type mappings.
        return {
            "settings": {
                "analysis": {
                    "filter": {
                        "autocomplete_filter": {
                            "type": "ngram",
                            "min_gram": 3,
                            "max_gram": 20
                        }
                    },
                    "analyzer": {
                        "autocomplete_analyzer": {
                            "type": "custom",
                            "tokenizer": "keyword",
                            "filter": [
                                "lowercase",
                                "autocomplete_filter"
                            ]
                        },
                        "autocomplete_query_analyzer": {
                            "type": "custom",
                            "tokenizer": "keyword",
                            "filter": [
                                "lowercase"
                            ]
                        }
                    }
                }
            },
              "mappings": {
                 self.doc_type: {
                    "properties": {
                       "lang": {
                          "type": "string"
                       },
                       "title": {
                          "type": "string",
                            "index_analyzer": "autocomplete_analyzer",
                            "search_analyzer": "autocomplete_query_analyzer"
                       },
                       "boost": {
                        "type": "float"
                    }
                }
             }
          }
        }

    def get_extra_state(self):
        # We want to rebuild this index whenever another index changes.
        aliases = self.get_alias_to_index_mapping()
        # Don't include own index in state as that would result in a loop
        if self.index_alias in aliases:
            aliases.pop(self.index_alias)
        return aliases
    
    def update_data(self):
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

        # Reduce entries to unique title, lang combination
        # and keep track of boost scores.
        entries = defaultdict(list)
        for entry in text_titles:
            key = (entry['heading.title'], entry['lang'])
            entries[key].append(entry['boost'])
        for entry in sutta_titles:
            key = (entry['name'], entry['lang'])
            entries[key].append(entry['boost'])
            
        actions = ({"title": k[0].replace('\xad', ''),
                    "lang": k[1],
                    "boost": 0.33 * (2 * max(v) + sum(v) / len(v))} for k,v in entries.items())

        self.process_actions(actions)

def search(query, limit, **params):
    body = {
        "size": limit,
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
    res = es.search('autocomplete', body=body)
    return {
        'took': res['took'],
        'total': res['hits']['total'],
        'hits': [
            {
                'score': hit['_score'],
                'value': hit['_source']['title'],
                'lang': hit['_source']['lang']
             }
             for hit in res['hits']['hits']
            ]
        }

def update():
    indexer = AutocompleteIndexer('autocomplete')
    indexer.update()

def periodic_update(i):
    if not sc.search.is_available():
        logger.error('Elasticsearch Not Available')
        return
    update()
