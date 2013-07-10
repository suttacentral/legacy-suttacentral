import cherrypy, os
import config, show

# We expose everything we need to here.

def error_page_404(status, message, traceback, version):
    return open(os.path.join(config.static_root, '404.html'), 'r').read()

class Root(object):

    _cp_config = {
        'error_page.404': error_page_404
    }

    @cherrypy.expose
    def default(self, *args, **kwargs):
        return show.default(*args, **kwargs)

    @cherrypy.expose
    def search(self, **kwargs):
        return show.search(**kwargs)

    @cherrypy.expose
    def index(self):
        return show.home()
