import json
import regex
import logging

import elasticsearch
from sc.search import es
logger = logging.getLogger(__name__)

def search(query, highlight=True, offset=0, limit=10,
            lang=None, define=None, details=None, **kwargs):
    # For some reason seems to require extra escaping to
    # resolve things like 'sati"'
    query = query.replace('define:', 'term:')
    indexes = ['en', 'en-dict', 'pi', 'suttas']
    doc_type = None
    if details is not None:
        doc_type = 'sutta'
        indexes = ['suttas']
    elif define is not None:
        doc_type = 'definition'
        indexes = ['en-dict']
    elif lang:
        indexes = [lang]
        doc_type = 'text'
    index_string = ','.join(index
                            for index in indexes
                            if es.cluster.health(index, timeout='0.01s')['status']
                            in {'green', 'yellow'})
    body = {
        "from": offset,
        "size": limit,
        "_source": ["uid", "lang", "name", "volpage", "gloss", "term", "heading", "is_root"],
        "timeout": "15s",
        "query": {
            "function_score": {
                "query": {
                    "multi_match": {
                        "type": "best_fields",
                        "tie_breaker": 0.3,
                        "fields": ["content", "content.*^0.5",
                                   "term^1.5", "term.*^0.5",
                                   "gloss^1.5",
                                   "lang^0.5",
                                   "author^0.5",
                                   "uid", "uid.division^0.7",
                                   "name^1.25", "name.*^0.75",
                                   "heading.title^0.5",
                                   "heading.title.plain^0.5",
                                   "heading.title.shingle^0.5"],
                        "query": query
                    }
                },
                "functions": [
                    {
                        "boost_factor": "1.2",
                        "filter": {
                            "term": {
                                "lang": "en"
                            }
                        }
                    },
                    {
                        "field_value_factor": {
                            "field": "boost",
                            "factor": 1
                        }
                    },                            
                    {
                        "boost_factor": "0.25",
                        "filter": {
                          "type": {
                              "value": "definition"
                          }
                        }
                    },
                    {
                        "boost_factor": "2",
                        "filter": {
                            "term": {
                                "uid": query.replace(' ', '').lower()
                            }
                        }
                    },
                    {
                        "boost_factor": "1.2",
                        "filter": {
                            "term": {
                                "is_root": True
                            }
                        }
                    }
                ],
                "score_mode": "multiply"
            }
        }
    }
    
    if highlight:
        body["highlight"] = {
            "pre_tags": ["<strong class=\"highlight\">"],
            "post_tags": ["</strong>"],
            "order": "score",
            "require_field_match": False,
            "fields": {
                "content" : {
                    "matched_fields": ["content", "content.folded", "content.stemmed"],
                    "type": "fvh",
                    "fragment_size": 100,
                    "number_of_fragments": 3,
                    "no_match_size": 250
                    }
                }
            }
    try:
        return es.search(index=index_string, doc_type=doc_type, body=body)
    except elasticsearch.exceptions.RequestError as e:
        # In case of an error, we'll repeat the query but with any
        # punctuation removed.
        new_query = regex.sub(r'\p{punct}', ' ', query)
        body['query']['function_score']['query']['query_string']['query'] = new_query
        return es.search(index=index_string, doc_type=doc_type, body=body)
