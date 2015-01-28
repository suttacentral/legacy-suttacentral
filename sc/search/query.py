import logging, json

from sc.search import es
logger = logging.getLogger(__name__)


def search(query, highlight=True, offset=0, limit=10, **kwargs):
    # For some reason seems to require extra escaping to
    # resolve things like 'sati"'
    query = query.replace('"', '\\"')
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
                                   "lang^0.5",
                                   "author^0.5",
                                   "uid", "uid.expanded^0.5",
                                   "name"],
                        "minimum_should_match": "3<90%",
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
    return es.search(body=body)
