import json
import logging

import elasticsearch
from sc.search import es
logger = logging.getLogger(__name__)


def search(query, highlight=True, offset=0, limit=10, **kwargs):
    # For some reason seems to require extra escaping to
    # resolve things like 'sati"'
    body = {
        "from": offset,
        "size": limit,
        "_source": ["uid", "lang", "name", "volpage", "gloss", "term", "heading"],
        "min_score": 0.33,
        "query": {
            "function_score": {
                "query": {
                    "query_string": {
                        "lenient": True,
                        "fields": ["content", "content.*^0.5",
                                   "term^1.5", "term.*^0.5",
                                   "gloss^1.5",
                                   "lang^0.5",
                                   "author^0.5",
                                   "uid", "uid.expanded^0.5",
                                   "name"],
                        "minimum_should_match": "100%",
                        "analyze_wildcard": True,
                        "query": query
                    }
                },
                "functions": [
                    {
                        "boost_factor": "1.1",
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
                        "boost_factor": "1.1",
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
        return es.search(body=body)
    except elasticsearch.exceptions.RequestError as e:
        body['query']['function_score']['query']['query_string']['query'] = query.replace('"', ' ')
        return es.search(body=body)
