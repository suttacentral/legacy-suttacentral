import logging
import requests
from elasticsearch.exceptions import NotFoundError, ConnectionError
import time
import regex
import lxml.html

import sc
import sc.logger
from sc.search.indexer import ElasticIndexer
from sc.search import es

logger = sc.logger.get_named_logger(__name__)

discourse_index = 'discourse'
es = ElasticIndexer.es

discourse_is_available = (sc.search.is_available()
                          and sc.config.discourse['api_key']
                          and sc.config.discourse['username']
                          and sc.config.discourse['forum_url'])
        

class DiscourseIndexer(ElasticIndexer):
    # Different doc types are possible.
    doc_type = None 
    version = 0
    suppress_elasticsearch_errors = True
    def __init__(self):
        super().__init__(config_name=discourse_index)
        self.latest_timestamp = ''
        self.forum_url = sc.config.discourse['forum_url']    
        if not self.forum_url.endswith('/'):
            self.forum_url += '/'
        
        self.qs_params = {
            "api_key": sc.config.discourse['api_key'],
            "api_username": sc.config.discourse['username']
        }
        self.connect()
    
    def to_plain_text(self, html_string):
        root = lxml.html.fromstring(html_string)
        return root.text_content().strip()
    
    def get_extra_state(self):
        stamp = int(time.time() % sc.config.discourse['rebuild_period'])
        return {"rebuild_number": stamp}
    
    def connect(self):
        r = requests.get(self.forum_url, params=self.qs_params)
        self.session_cookie = r.cookies['_forum_session']
    
    latest_update_query =   {
                                "query": {
                                    "match_all": {}
                                },
                                "size": 1,
                                "sort": [
                                    {
                                        "updated_at": {
                                            "order": "desc"
                                        }
                                    }
                                ]
                            }
    
    def get_data(self, params=None):
        if not params:
            params = {}
        
        if 'since' not in params:
            if self.latest_timestamp:
                params['since'] = self.latest_timestamp
            else:
                try:
                    r = self.es.search(self.index_name,body=self.latest_update_query, _source='updated_at')
                    params["since"] = r['hits']['hits'][0]['_source']['updated_at']
                except Exception as e:
                    params["since"] = '1900-01-01T00:00:00.000Z'
        
        params.update(self.qs_params)
        
        r = requests.get(self.forum_url + 'sutcen/data.json', 
                         params=params,
                         cookies={'_forum_session': self.session_cookie}
                         )
        self.r = r
        return r.json()
    
    def update_data(self):
        most_recent = None
        params = {}
        if most_recent:
            params['since'] = most_recent
        data = self.get_data(params)
        logger.info('New categories: {}, new topics: {}, new posts: {}'.format(len(data['categories']),
                                                                               len(data['topics']),
                                                                               len(data['posts'])))
        actions = self.yield_actions(data)
        actions = self.log_and_reyield_actions(actions)
        actions = self.update_time_stamp_and_reyield_actions(actions)
        self.actions = actions
        self.process_actions(actions)                    
    
    def update_time_stamp_and_reyield_actions(self, actions):
        for action in actions:
            updated_at = action['_source'].get('updated_at')
            deleted_at = action['_source'].get('deleted_at')
            if updated_at:
                if updated_at > self.latest_timestamp:
                    self.latest_timestamp = updated_at
            if deleted_at:
                if deleted_at > self.latest_timestamp:
                    self.latest_timestamp = deleted_at
            yield action
                    
    
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
        
        def is_visible(obj):
            if 'deleted_at' in obj and obj['deleted_at']:
                return False
            if 'hidden' in obj and obj['hidden']:
                return False
            
            if 'topic_id' in obj:
                topic = topics[obj['topic_id']]
                if topic['deleted_at']:
                    return False
                elif topic['read_restricted']:
                    return False
        
        def category_is_visible(category):
            if category['read_restricted']:
                return False
            parent_id = category['parent_category_id']
            if parent_id:
                try:
                    parent = categories[parent_id]
                except KeyError:
                    try:
                        parent = self.es.get(index=self.index_name, doc_type='category', id=parent_id)['_source']
                    except NotFoundError:
                        return False
                return category_is_visible(parent)
            else:
                return True
        
        def topic_is_visible(topic):
            if topic['deleted_at']:
                return False
            try:
                category = categories[topic['category_id']]
            except KeyError:
                try:
                    category = self.es.get(index=self.index_name, doc_type='category', id=topic['category_id'])['_source']
                except NotFoundError:
                    return False
            #category = categories[topic['category_id']]
            return category_is_visible(category)
        
        def post_is_visible(post):
            if post['deleted_at'] or post['hidden']:
                return False
            try:
                topic = topics[post['topic_id']]
            except KeyError:
                try:
                    topic = self.es.get(index=self.index_name, doc_type='topic', id=post['topic_id'])['_source']
                except NotFoundError:
                    return False
            return topic_is_visible(topic)
        
        def delete_posts(topic_id):
            query = {
                        "query": {
                            "term": {
                                "topic_id": topic_id
                            }
                        }
                    }
            results = self.es.search(self.index_name, 'post', body=query, source=['id'])
            for hit in results['hits']:
                post_id = hit['_source']['id']
                action = {'_type': 'post', '_id': post_id}
                action['_op_type'] = 'delete'
                yield action
            
        
        for category in data['categories']:
            action = {'_type': 'category', 
                      '_id': category['id'],
                      '_source': category}
            if not category_is_visible(category):
                action['_op_type'] = 'delete'
            yield action
            
        for topic in data['topics']:
            if topic['category_id'] is None:
                topic['category_id'] = 1
            action = {'_type': 'topic',
                      '_id': topic['id'],
                      '_source': topic}
            if not topic_is_visible(topic):
                action['_op_type'] = 'delete'
                delete_posts(topic['id'])
            yield action
        
        for post in data['posts']:
            action = {'_type': 'post',
                      '_id': post['id'],
                      '_source': post}
            if post_is_visible(post):
                post['plain'] = self.to_plain_text(post['cooked'])
                action['_parent'] = post['topic_id']
            else:
                action['_op_type'] = 'delete'
            yield action
     except:
         self.locs = locals()
         raise

def update(force=False, _indexer=[]):
    if not discourse_is_available:
        return
    if not _indexer:
        _indexer.append(DiscourseIndexer())
    _indexer[0].update()

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
    uid = uid.lower()
    body = {
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
                    "_source": ["post_number", "id"],
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
                                    "filtered": {
                                      "filter": {
                                        "term": {
                                          "topic_id": hit['_source']['id']
                                        }
                                      }
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
            
