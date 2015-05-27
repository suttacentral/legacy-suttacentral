import json
import cherrypy


import sc
from sc import show, donations
from sc.tools import webtools

# We expose everything we need to here.
    

def get_cookie_or_param(name):
    if name in cherrypy.request.cookie:
        return cherrypy.request.cookie[name].value
    elif name in cherrypy.request.params:
        return cherrypy.request.params[name]
    else:
        return None

def remove_trailing_slash():
    request = cherrypy.serving.request
    path = request.path_info
    if path != '/' and path.endswith('/'):
        url = cherrypy.url(path[:-1], request.query_string)
        raise cherrypy.HTTPRedirect(url, 301)

def set_offline():
    if get_cookie_or_param('offline'):
        offline = True
    else:
        offline = False
    cherrypy.request.offline = offline

cherrypy.tools.remove_trailing_slash = cherrypy.Tool('before_handler',
    remove_trailing_slash)
cherrypy.tools.set_offline = cherrypy.Tool('before_handler', set_offline)

class Root(object):
    """Requests to /*"""

    _cp_config = {
        'error_page.default': show.error,
        'tools.trailing_slash.on': False,
        'tools.remove_trailing_slash.on': True,
        'tools.set_offline.on': True,
    }

    def __init__(self):
        self.admin = Admin()
        if not sc.config.disable_tools:
            self.tools = webtools.Tools()
        
        if sc.config.app['yappi_profiling']:
            from sc.profiler import profiler
            self.profiler = profiler
            profiler.start()

    @cherrypy.expose
    def default(self, *args, **kwargs):
        cherrypy.serving.request.cacheable = False
        if 'profile' in kwargs:
            try:
                return show.profile(locals(), globals(), *args, **kwargs)
            except ValueError:
                pass
        return show.default(*args, **kwargs)

    @cherrypy.expose
    def search(self, **kwargs):
        return show.search(**kwargs)
    
    @cherrypy.expose
    def advanced_search(self, **kwargs):
        return show.advanced_search(**kwargs)
    
    @cherrypy.expose
    def sutta_info(self, uid, lang='en', **kwargs):
        return show.sutta_info(uid, lang)
    
    @cherrypy.expose
    @cherrypy.tools.json_out()
    def data(self, **kwargs):
        " Endpoint which return JSON data "
        return show.data(**kwargs)
    
    @cherrypy.expose
    def index(self, **kwargs):
        return show.home()

    @cherrypy.expose
    def downloads(self, **kwargs):
        return show.downloads()

    @cherrypy.expose
    def sht_lookup(self, query, **kwargs):
        return show.sht_lookup(query)

    @cherrypy.expose
    def define(self, term, **kwargs):
        term = term.encode(encoding='latin-1').decode(encoding='utf8')
        return show.define(term)
    
    @cherrypy.expose
    def donate(self, page, **kwargs):
        if cherrypy.request.method != 'POST':
            raise cherrypy.NotFound()
        return show.donate(page, **kwargs)

class Admin(object):
    """Requests to /admin/*"""

    @cherrypy.expose
    def index(self, **kwargs):
        return show.admin_index()

    @cherrypy.expose
    def data_notify(self, **kwargs):
        return show.admin_data_notify(kwargs.get('payload'))
