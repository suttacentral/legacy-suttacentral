import json
import regex
import logging

import elasticsearch
from sc.search import es
logger = logging.getLogger(__name__)

def div_translation_count(lang):
    " Returns the count of translations per subdivision "
    body = {
        'aggregations': {
            'div_uids': {
                'terms': {
                    'field': 'division',
                    'size': 0 # Unlimited
                }
            },
            'subdiv_uids': {
                'terms': {
                    'field': 'subdivision',
                    'size': 0 # Unlimited
                }
            }
        }
    }
    try:
        result = es.search(index=lang, doc_type='text', search_type='count', body=body)
    except elasticsearch.exceptions.NotFoundError:
        return None
    mapping = {d['key']: d['doc_count']
            for d
            in result['aggregations']['subdiv_uids']['buckets']}

    # If division and subdiv is shared, clobber with div value.
    mapping.update({d['key']: d['doc_count']
            for d
            in result['aggregations']['div_uids']['buckets']})
    return mapping

def search(query, highlight=True, offset=0, limit=10,
            lang=None, define=None, details=None, **kwargs):
    query.strip()
    indexes = []
    if details is not None:
        indexes = ['suttas']
    if define is not None:
        indexes.append('en-dict')
    if lang:
        indexes.append(lang)

    if not indexes:
        indexes = ['en', 'pi', 'suttas', 'en-dict']

    index_string = ','.join(index
                            for index in indexes
                            if es.cluster.health(index, timeout='0.01s')['status']
                            in {'green', 'yellow'})
    
    fields =  ["content", "content.*^0.5",
               "term^1.5", "term.*^0.5",
               "gloss^1.5",
               "lang^0.5",
               "author^0.5",
               "uid", "uid.division^0.7",
               "name^1.25", "name.*^0.75",
               "heading.title^0.5",
               "heading.title.plain^0.5",
               "heading.title.shingle^0.5"]
    
    if (regex.search(r'[:"~*]', query) or regex.search(r'AND|OR|NOT', query)):
        query = query.replace('define:', 'term:')
        inner_query = {
            "query_string": {
                "fields": fields,
                "query": query,
                "use_dis_max" : True
            }
        }
    else:
        inner_query = {
            "multi_match": {
                "type": "best_fields",
                "tie_breaker": 0.3,
                "fields": fields,
                "query": query
            }
        }
    
    body = {
        "from": offset,
        "size": limit,
        "_source": ["uid", "lang", "name", "volpage", "gloss", "term", "heading", "is_root"],
        "timeout": "15s",
        "query": {
            "function_score": {
                "query": inner_query,
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
    import json
    print(json.dumps(body, indent=2))
    
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
    
    return es.search(index=index_string, body=body)
    
