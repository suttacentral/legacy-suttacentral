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
    index = "en,pi,suttas"
    doc_type = None
    if details is not None:
        doc_type = 'sutta'
        index = 'suttas'
    elif define is not None:
        doc_type = 'definition'
        index = 'en'
    elif lang:
        index = lang
        doc_type = 'text'
    print('Index = {}, lang = {}'.format(index, lang))
    
    body = {
        "from": offset,
        "size": limit,
        "_source": ["uid", "lang", "name", "volpage", "gloss", "term", "heading", "is_root"],
        "timeout": "15s",
        "query": {
            "function_score": {
                "query": {
                    "multi_match": {
                        "type": "cross_fields",
                        "fields": ["content", "content.*^0.5",
                                   "term^1.5", "term.*^0.5",
                                   "gloss^1.5",
                                   "lang^0.5",
                                   "author^0.5",
                                   "uid", "uid.division^0.7",
                                   "name", "name.*^0.75"],
                        "minimum_should_match": "99%",
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
        return es.search(index=index, doc_type=doc_type, body=body)
    except elasticsearch.exceptions.RequestError as e:
        # In case of an error, we'll repeat the query but with any
        # punctuation removed.
        new_query = regex.sub(r'\p{punct}', ' ', query)
        body['query']['function_score']['query']['query_string']['query'] = new_query
        return es.search(index=index, doc_type=doc_type, body=body)
