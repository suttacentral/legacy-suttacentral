import logging
import requests
from elasticsearch.exceptions import NotFoundError

import sc, sc.scimm
import sc.logger
from sc.search.indexer import ElasticIndexer

logger = logging.getLogger(__name__)
handler = sc.logger.file_handler(__name__)
logger.addHandler(handler)
logger.setLevel('INFO')
handler.setLevel('INFO')

class DiscourseIndexer(ElasticIndexer):
    # Different doc types are possible.
    doc_type = None 
    def __init__(self):
        super().__init__(config_name='discourse')
        
        self.forum_url = sc.config.discourse['forum_url']    
        if not self.forum_url.endswith('/'):
            self.forum_url += '/'
        
        self.qs_params = {
            "api_key": sc.config.discourse['api_key'],
            "api_username": sc.config.discourse['username']
        }
        self.connect()
        
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
            try:
                r = self.es.search('discourse',body=self.latest_update_query, _source='updated_at')
                params["since"] = r['hits']['hits'][0]['_source']['updated_at']
            except Exception as e:
                logger.exception('Failed to retrieve updated_at from index')
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
        actions = self.log_and_yield_actions(actions)
        self.actions = actions
        from elasticsearch.helpers import bulk
        bulk(self.es, index='discourse', actions=actions)
    
    def log_and_yield_actions(self, actions):
        for action in actions:
            try:
                
                logger.info('{}: {_type}/{_id}'.format(action.get('_op_type', 'index'),**action))
            except:
                print(action)
                raise
            yield action
    
    def yield_actions(self, data):
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
            return not category['read_restricted']
        
        def topic_is_visible(topic):
            if topic['deleted_at']:
                return False
            #try:
                #category = categories[topic['category_id']]
            #except KeyError:
                #try:
                    #category = es.get(index=self.index_name, doc_type='category', id=topic['category_id'])
                #except NotFoundError:
                    #return False
            category = categories[topic['category_id']]
            return category_is_visible(category)
        
        def post_is_visible(post):
            if post['deleted_at'] or post['hidden']:
                return False
            #try:
                #topic = topics[post['topic_id']]
            #except KeyError:
                #try:
                    #topic = es.get(index=self.index_name, doc_type='topic', id=post['topic_id'])['_source']
                #except NotFoundError:
                    #return False
            topic = topics[post['topic_id']]
            return topic_is_visible(topic)
        
        for category in data['categories']:
            action = {'_type': 'category', '_id': category['id']}
            if category_is_visible(category):
                action.update(category)
            else:
                action.update(category)
                action['_op_type'] = 'delete'
            yield action
            
        for topic in data['topics']:
            action = {'_type': 'topic', '_id': topic['id']}
            if topic_is_visible(topic):
                action.update(topic)
            else:
                action.update(topic)
                action['_op_type'] = 'delete'
            yield action
        
        for post in data['posts']:
            action = {'_type': 'post', '_id': post['id']}
            if post_is_visible(post):
                action.update(post)
            else:
                action.update(post)
                action['_op_type'] = 'delete'
            yield action
        
indexer = DiscourseIndexer()


def update(force=False):
    def sort_key(d):
        if d.stem == 'en':
            return 0
        if d.stem == 'pi':
            return 1
        return 10
    lang_dirs = sorted(sorted(sc.text_dir.glob('*')), key=sort_key)

    for lang_dir in lang_dirs:
        if lang_dir.is_dir():
            indexer = TextIndexer(lang_dir.stem, lang_dir)
            indexer.update()

def periodic_update(i):
    if not sc.search.is_available():
        logger.error('Elasticsearch Not Available')
        return
    update()
