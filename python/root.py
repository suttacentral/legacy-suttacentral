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
    def index(self, **kwargs):
        return show.home()

    # Redirect for old site URL: disp_correspondence.php?sutta_id=...
    @cherrypy.expose
    def disp_correspondence_php(self, **kwargs):
        return show.fallback_disp_correspondence(**kwargs)

    # Redirect for old site URL: disp_division.php?collection_id=...
    @cherrypy.expose
    def disp_division_php(self, **kwargs):
        raise cherrypy.HTTPRedirect('/', 302)

    # Redirect for old site URL: disp_subdivision.php?division_id=...
    @cherrypy.expose
    def disp_subdivision_php(self, **kwargs):
        return show.fallback_disp_subdivision(**kwargs)

    # Redirect for old site URL: disp_sutta.php?division_id=... or
    #                            disp_sutta.php?subdivision_id=...
    @cherrypy.expose
    def disp_sutta_php(self, **kwargs):
        return show.fallback_disp_sutta(**kwargs)

