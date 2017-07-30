import time
import logging
import weakref
import requests
import functools

import sc

logger = logging.getLogger(__name__)


discourse_is_available = (sc.search.is_available()
                          and sc.config.discourse['api_key']
                          and sc.config.discourse['username']
                          and sc.config.discourse['forum_url'])

class BadResponseError(Exception):
    pass

def cached(*lru_args, **lru_kwargs):
    def decorator(func):
        @functools.wraps(func)
        def wrapped_func(self, *args, **kwargs):
            # We're storing the wrapped method inside the instance. If we had
            # a strong reference to self the instance would never die.
            self_weak = weakref.ref(self)
            @functools.wraps(func)
            @functools.lru_cache(*lru_args, **lru_kwargs)
            def cached_method(*args, **kwargs):
                return func(self_weak(), *args, **kwargs)
            setattr(self, func.__name__, cached_method)
            return cached_method(*args, **kwargs)
        return wrapped_func
    return decorator

class Discourse:
    _cache = None
    def __init__(self, forum_url, username, api_key):
        
        self._cache = {}
        if not forum_url.endswith('/'):
            forum_url += '/'
        
        self.forum_url = forum_url
        self.username = username
        self.api_key = api_key
        
        
        self.qs_params = {
            "api_key": api_key,
            "api_username": username
        }
        
        r = requests.get(self.forum_url, params=self.qs_params)
       
    def get(self, path):
        r = requests.get(self.forum_url + path, params=self.qs_params)
        if 200 >= r.status_code < 300:
            return r
        else:
            msg = f'{r.status_code} error ({r.reason}) for url {path}'
            raise ConnectionError(msg)
            
    
    def category_is_visible(self, category, categories):
        if category['read_restricted']:
            return False
        if category['name'] in {'Meta', 'Feedback', 'Uncategorized', 'The Watercooler', 'Wiki'}:
            return False
        if 'parent_category_id' in category:
            parent_id = category['parent_category_id']
        
            try:
                parent = categories[parent_id]
            except KeyError:
                return False
            return self.category_is_visible(parent, categories)
        else:
            return True
    
    @cached()
    def category(self, id):
        return self.categories()[id]
    
    @cached()
    def categories(self):
        site = self.site()
        raw_categories = {e['id']: e for e in site['categories'] }
        return {e['id']: e for e in raw_categories.values() if self.category_is_visible(e, raw_categories)}
    
    @cached()
    def site(self):
        try:
            r = self.get('site.json')
            return r.json()
        except BadResponseError as e:
            logging.error(e.msg)
            raise
            
    
    def get_topics_in_category(self, category_id):
        category = self.categories()[category_id]
    
        print(f'Now downloading category: {category["name"]}')
        
        def process_category_results(uri):
            print(f'Using URI: {uri}')
            r = self.get(uri)
            j = r.json()
            topic_list = j['topic_list']
            topics = topic_list['topics']
            try:
                more_topics_url = topic_list['more_topics_url']
                if '.json' not in more_topics_url:
                    more_topics_url = more_topics_url.replace('?', '.json?')
            except KeyError:
                more_topics_url = None
            
            
            for topic in topics:
                print(f'Downloading topic {topic["id"]}: {topic["title"]}: {topic["tags"]!s}')
                yield topic
            if more_topics_url:
                yield from process_category_results(more_topics_url)

        if 'parent_category_id' in category:
            uri = f'c/{category["parent_category_id"]}/{category_id}.json'
        else:
            uri = f'c/{category_id}.json'
            
        yield from process_category_results(uri)
    
    def process_topic(self, topic_id, post_count=1):
        topic = self.get(f't/{topic_id}.json').json()
        post_stream = topic['post_stream']
        
        params = ('id', 'title', 'tags', 'slug', 'created_at', 'reply_count', 'category_id')
        
        out = {param: topic[param] for param in params}
        
        posts = post_stream['posts']
        if posts:
            out['posts'] = [posts[0]['cooked']]
            
        return out


def get_discourse():
    return Discourse(forum_url=sc.config.discourse['forum_url'],
                        username=sc.config.discourse['username'],
                        api_key=sc.config.discourse['api_key'])
    
    
    
