import logging
from collections import defaultdict

from elasticsearch import Elasticsearch
from elasticsearch.helpers import scan

import sc.search

from sc.search.indexer import ElasticIndexer

logger = logging.getLogger(__name__)

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
                            "tokenizer": "standard",
                            "filter": [
                                "lowercase",
                                "autocomplete_filter"
                            ]
                        },
                        "autocomplete_query_analyzer": {
                            "type": "custom",
                            "tokenizer": "standard",
                            "filter": [
                                "lowercase"
                            ]
                        },
                        "folding_analyzer": {
                            "tokenizer": "icu_tokenizer",
                            "filter": ["icu_folding"]
                        },
                        "autocomplete_folding_analyzer": {
                            "tokenizer": "icu_tokenizer",
                            "filter": ["icu_folding",
                                        "autocomplete_filter"]
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
                            "index_analyzer": "autocomplete_analyzer",
                            "search_analyzer": "autocomplete_query_analyzer",
                            "fields": {
                                "lowercase": {
                                    "type": "string",
                                    "analyzer": "lowercase_keyword"
                                },
                                "plain": {
                                    "type": "string",
                                    "analyzer": "folding_analyzer"
                                },
                                "folded": {
                                    "type": "string",
                                    "analyzer": "autocomplete_folding_analyzer"
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
    
    def is_updated_needed(self):
        # Always completely rebuild index if data changes
        if not self.index_exists():
            return True
        if not self.alias_exists():
            return True
        return False
    
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

        # Reduce entries to unique title, lang combination
        # and keep track of boost scores.
        entries = defaultdict(list)
        for entry in text_titles:
            key = (entry['heading.title'], entry['lang'])
            entries[key].append(entry['boost'])
        for entry in sutta_titles:
            key = (entry['name'], entry['lang'])
            entries[key].append(entry['boost'])
        actions = ({"_id": '{}_{}'.format(k[0], k[1]),
                    "length": len(k[0]),
                    "title": k[0],
                    "lang": k[1],
                    "boost": 0.33 * (2 * max(v) + sum(v) / len(v))} for k,v in entries.items())

        self.process_actions(actions)

def search(query, limit, **params):
    body = {
        "size": limit,
        "query": {
            "function_score": {
                "query": {
                    "multi_match": {
                        "fields": ["title", "title.folded^0.5"],
                        "query": query
                    }
                },
                "functions": [
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
                                "lang": ["en"]
                            }
                        },
                        "weight": 1.4
                    },
                    {
                    "exp": {
                        "length": {
                                "origin": 6,
                                "scale": 7
                            }
                        }
                    }
                ],
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

def periodic_update(i):
    if not sc.search.is_available():
        logger.error('Elasticsearch Not Available')
        return
    update()
