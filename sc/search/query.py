import logging

from sc.search import es
logger = logging.getLogger(__name__)


def search(query, highlight=True, offset=0, limit=10, **kwargs):
    body = {
        "from": offset,
        "size": limit,
        "_source": ["uid", "lang", "name", "volpage", "gloss", "term", "heading"],
        "query": {
            "function_score": {
                "query": {
                    "query_string": {
                        "fields": ["content", "content.*^0.5",
                                   "term", "term.*^0.5",
                                   "lang",
                                   "uid",
                                   "acro",
                                   "name"],
                        "minimum_should_match": "3<90%",
                        "analyze_wildcard": True,
                        "query": query
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
                    "number_of_fragments": 3
                    }
                }
            }
    return es.search(body=body)
