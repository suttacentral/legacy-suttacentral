import logging
from collections import defaultdict

from elasticsearch import Elasticsearch
from elasticsearch.helpers import scan

import sc.search

from sc.search.indexer import ElasticIndexer

logger = logging.getLogger('search.autocomplete')

class AutocompleteIndexer(ElasticIndexer):
    doc_type = 'autocomplete'
    version = 2

    def load_index_config(self, config_name):
        # Altough get_index_config normally loads a file
        # here we just define the index settings and mapping inline
        # as it is so very different and vastly simpler than the
        # the other type mappings.
        return {
            "settings": {
                "analysis": {
                    "filter": {
                        "autocomplete_ngram_filter": {
                            "type": "ngram",
                            "min_gram": 3,
                            "max_gram": 20
                        }
                    },
                    "analyzer": {
                        "autocomplete_ngram_analyzer": {
                            "type": "custom",
                            "tokenizer": "standard",
                            "filter": [
                                "icu_folding",
                                "autocomplete_ngram_filter"
                            ]
                        },
                        "autocomplete_query_analyzer": {
                            "type": "custom",
                            "tokenizer": "standard",
                            "filter": [
                                "icu_folding"
                            ]
                        },
                        "lowercase_keyword": {
                            "tokenizer": "keyword",
                            "filter": ["lowercase"]
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
                            "index_analyzer": "autocomplete_ngram_analyzer",
                            "search_analyzer": "autocomplete_query_analyzer",
                            "fields": {
                                "lowercase": {
                                    "type": "string",
                                    "analyzer": "lowercase_keyword"
                                },
                                "plain": {
                                    "type": "string",
                                    "analyzer": "standard"
                                }
                            }
                       },
                       "boost": {
                            "type": "float"
                        },
                        "length": {
                            "type": "integer"
                        }
                    }
                }
            } 
        }

    def get_extra_state(self):
        # We want to rebuild this index whenever another index changes.
        aliases = self.get_alias_to_index_mapping(exclude_prefix=self.index_prefix)
        return aliases
    
    def update_data(self):
        es = self.es
        # Extract text titles
        text_titles = [{k.replace('\xad', ''):v[0] for k,v in hit['fields'].items()} for hit in scan(es,
            index='_all',
            doc_type="text",
            fields=["uid", "lang", "boost", "heading.title"],
            query=None,
            size=500)]

        # Extract sutta titles
        sutta_titles = [{k.replace('\xad', ''):v[0] for k,v in hit['fields'].items()} for hit in scan(es,
            index='suttas',
            doc_type='sutta',
            fields=['uid', 'lang', "boost", 'name'],
            size=500)]

        term_titles = [{k:v[0] for k,v in hit['fields'].items()} for hit in scan(es,
            index='_all',
            doc_type='definition',
            fields=['term', 'lang', 'boost'],
            size=500)]

        # Reduce entries to unique title, lang combination
        # and keep track of boost scores.
        entries = defaultdict(list)
        for entry in text_titles:
            try:
                key = (entry['heading.title'], entry['lang'])
                entries[key].append(entry['boost'])
            except KeyError:
                pass
        for entry in sutta_titles:
            key = (entry['name'], entry['lang'])
            entries[key].append(entry['boost'])
        for entry in term_titles:
            key = (entry['term'], entry['lang'])
            entries[key].append(entry['boost'])
        
        actions = ({"_id": '{}_{}'.format(k[0], k[1]),
                    "length": len(k[0]),
                    "title": k[0],
                    "lang": k[1],
                    "boost": v} for k,v in entries.items())

        self.process_actions(actions)

def search(query, limit, lang=None, **params):
    functions = [
        {
            "field_value_factor": {
                "field": "boost"
            }
        },
        {
            "filter": {
                "prefix": {
                    "title.plain": query
                }
            },
            "weight": 2
        },
        {
            "filter": {
                "prefix": {
                    "title.lowercase": query
                }
            },
            "weight": 2
        },
        {
            "filter": {
                "terms": {
                    "lang": ["pi"]
                }
            },
            "weight": 1.8
        },
        {
            "filter": {
                "terms": {
                    "lang": [lang or 'en']
                }
            },
            "weight": 1.5
        },
        {
        "exp": {
            "length": {
                    "origin": 6,
                    "scale": 7
                }
            }
        }
    ]
        
    body = {
        "size": limit,
        "query": {
            "function_score": {
                "query": {
                    "match": {
                        "title": query
                    }
                },
                "functions": functions,
                "score_mode": "multiply"
            }
        }
    }
        
    res = sc.search.es.search('autocomplete', body=body)
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
