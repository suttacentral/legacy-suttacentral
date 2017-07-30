import logging
from elasticsearch.exceptions import NotFoundError, ConnectionError
import time
import regex
import lxml.html
import json
import sc
import sc.logger
from sc.search.indexer import ElasticIndexer
from sc.search import es

from sc.search.discourse_forum import Discourse

logger = sc.logger.get_named_logger(__name__)

discourse_index = 'discourse'
es = ElasticIndexer.es



class DiscourseIndexer(ElasticIndexer):
    # Different doc types are possible.
    doc_type = None 
    version = 1
    suppress_elasticsearch_errors = True
    def __init__(self, forum):
        super().__init__(config_name=discourse_index)
        self.forum = forum
    
    def to_plain_text(self, html_string):
        root = lxml.html.fromstring(html_string)
        return root.text_content().strip()
    
    def get_extra_state(self):
        stamp = time.time()
        return {"rebuild_time": stamp}
    
    def update_data(self, save_to_disk=False):
        categories = list(self.forum.categories())
        topics = []
        for category_id in categories:
            topics.extend(self.forum.get_topics_in_category(category_id))
            break
        posts = []
        time.sleep(1)
        for i, topic in enumerate(topics):
            if i % 100 == 0:
                print(f'Processing topic {i+1}/{len(topics)+1}')
            posts.append(self.forum.process_topic(topic["id"]))
            
        actions = self.log_and_reyield_actions(actions)
        self.actions = actions
        self.process_actions(actions)
        if save_to_disk:
            with pathlib.Path("data.json").open('w') as f:
                json.dump({
                    "categories": categories,
                    "topics": topics,
                    "posts": posts
                }, f, ensure_ascii=1)
    
    def log_and_reyield_actions(self, actions):
        for action in actions:
            self.action = action
            try:
                logger.info('{}: {_type}/{_id}'.format(action.get('_op_type', 'index'),**action))
            except:
                print(action)
                raise
            yield action
    
    def yield_actions(self, data):
     try:
        # Create indexes
        categories = {c['id']: c for c in data['categories']}
        topics = {t['id']: t for t in data['topics']}
        posts = {p['id']: p for p in data['posts']}
  
  

def update(force=False, _indexer=[]):
    if not discourse_is_available:
        return
    forum = sc.search.discourse_forum.get_discourse()
    indexer = DiscourseIndexer(forum=forum)

def make_snippet(plain_string, length=250):
    pattern = r'.{,%i}(?:[.!?,:;]|$)' % (length, )
    m = regex.match(pattern, plain_string)
    if m:
        return m[0]
    else:
        return ''    

def get_category(category_id):
    cat = es.get(discourse_index,
                         doc_type='category',
                         id=category_id)['_source']
    
    return {
        'id': cat['id'],
        'name': cat['name'],
        'description': cat['description'],
        'color': cat['color'],
        'text_color': cat['text_color'],
        'slug': cat['slug'],
        'parent_category_id': cat['parent_category_id']
    }

def search(uid):
    if not discourse_is_available:
        return None
    uid = uid.lower().split('-')[0]
    body = {
      "query": {
        "function_score": {
          "query": {
            "bool": {
              "should": [
                {
                  "has_child": {
                    "type": "post",
                    "score_mode": "sum",
                    "query": {
                      "match": {
                        "plain": uid
                      }
                    },
                    "inner_hits": {
                        "size": 1,
                       # "_source": ["post_number", "id"],
                        "highlight": {
                            "fields": {
                                "plain": {}
                            }
                        }
                    }
                  }
                },
                {
                  "match": {
                    "tags": uid
                  }
                },
                {
                  "match": {
                    "title": uid
                  }
                }
              ]
            }
          },
          "boost_mode": "sum",
          "functions": [
            {
              "gauss":{
                "updated_at": {
                    "origin": "now",
                    "scale": "21d",
                    "offset": "7d",
                    "decay":  0.5
                }
              },
              "weight": 2
            }
          ]
        }
      }
    }
    import json
    result = es.search(discourse_index, doc_type='topic', body=body)
    hits = result['hits']['hits']
    out = {
        'topics': [],
        'categories': {}
    }
    
    for hit in hits:
        inner_hits = hit['inner_hits']['post']['hits']['hits']
        if inner_hits:
            inner_hit = inner_hits[0]['_source']
            snippet = ' … '.join(inner_hits[0]['highlight']['plain'])
        else:
            first_post_query = {
                                  "size": 1,
                                  "query": {
                                        "term": {
                                          "topic_id": hit['_source']['id']
                                        }
                                  },
                                  "sort": [
                                    {
                                      "post_number": {
                                        "order": "asc"
                                      }
                                    }
                                  ]
                                }
                
            r = es.search(discourse_index,
                                  doc_type='post',
                                  body=first_post_query)
            inner_hits = r['hits']['hits']
            if inner_hits:
                inner_hit = inner_hits[0]['_source']
                snippet = make_snippet(inner_hit['plain'])
            else:
                inner_hit = None
                snippet = ''
        source = hit['_source']
        out['topics'].append({
            'topic_id': source['id'],
            'post_number': inner_hit['post_number'] if inner_hit else None,
            'title': source['title'],
            'category_id': source['category_id'],
            'snippet': snippet
        })
        if source['category_id'] not in out['categories']:
            cat = get_category(source['category_id'])
            out['categories'][cat['id']] = cat
            parent_id = cat['parent_category_id']
            if parent_id and parent_id not in out['categories']:
                parent_cat = get_category(parent_id)
                out['categories'][parent_cat['id']] = parent_cat
    return out
            
