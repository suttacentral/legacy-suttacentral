import cherrypy, os
import config, show

# We expose everything we need to here.

def error_page_404(status, message, traceback, version):
    return (config.static_dir / '404.html').open('r', encoding='utf-8').read()

def get_cookie_or_param(name):
    if name in cherrypy.request.cookie:
        return cherrypy.request.cookie[name].value
    elif name in cherrypy.request.params:
        return cherrypy.request.params[name]
    else:
        return None

def set_offline():
    if get_cookie_or_param('offline'):
        offline = True
    else:
        offline = False
    cherrypy.request.offline = offline

cherrypy.tools.set_offline = cherrypy.Tool('before_handler', set_offline)

class Root(object):

    _cp_config = {
        'error_page.404': error_page_404,
        'tools.set_offline.on': True,
    }

    @cherrypy.expose
    def default(self, *args, **kwargs):
        return show.default(*args, **kwargs)

    @cherrypy.expose
    def search(self, **kwargs):
        return show.search(**kwargs)

    @cherrypy.expose
    def index(self, **kwargs):
        return show.home()

    @cherrypy.expose
    def downloads(self, **kwargs):
        return show.downloads()

    @cherrypy.expose
    def sht_lookup(self, query, **kwargs):
        return show.sht_lookup(query)
