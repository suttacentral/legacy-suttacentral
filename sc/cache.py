import cherrypy
from cherrypy.lib.caching import MemoryCache

class Cache(MemoryCache):
    """ Cache that only caches certain pages

    Sutta Central division and subdivision pages require many database
    queries so tend to be quite time consuming to render.

    On the other hand, texts, of which there are bazillions, are for
    the most part simply loaded off the disk and are not time consuming
    at all to render.

    So this cache is configured to only cache the home page, division
    pages and subdivision pages.

    Some details pages may also be time consuming but are not cached
    for two reasons, first, they are not often referenced, secondly
    there are very many of them.

    If these measures were not taken, then crawlers crawling the texts
    would tend to invalidate the cache too often.

    """
    
    uids = None
    
    def _set_uids(self):
        import sc.scimm
        imm = sc.scimm.imm()

        self.uids = set()
        self.uids.update(imm.divisions)
        self.uids.update(imm.subdivisions)        
        
    def get(self):
        request = cherrypy.serving.request
        if hasattr(request, 'args') and request.args:
            if self.uids is None:
                self._set_uids()
            if len(request.args) > 1 or request.args[0] not in self.uids:
                request.cached = False
                request.cacheable = False
                return False

        return super().get()
