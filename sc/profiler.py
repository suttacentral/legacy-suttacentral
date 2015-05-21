import regex
import yappi
import cherrypy

from sc.views import GenericView

class Profiler:
    def start(self):
        yappi.start()
    
    def stop(self):
        yappi.stop()
    
    def clear(self):
        yappi.clear_stats()
    
    @cherrypy.expose
    def index(self, start=None, stop=None, clear=None, show=None):
        start = yappi.is_running() or start
        self.stop()
        result = None
        try:
            if show:
                stats = self.get_stats()
            else:
                stats = None
            if clear:
                self.clear()
            
            result = GenericView('profiler', {'stats': stats}).render()
        finally:
            if start:
                self.start()
        
        return result
        
    def get_stats(self):
        stats = yappi.get_func_stats()
        keys = next(iter(stats))._KEYS
        module_i = keys.index('module')
        out = []
        for s in stats:
            m = regex.match(r'.*/(python\d+\.\d+.*|sc/.*)', s.module)
            if m:
                module = m[1]
            else:
                module = module
            if module.startswith('python'):
                continue
            d = [s[i] for i in s]
            d[module_i] = module
            out.append(d)
        
        return {'fields': keys,
                'rows': out}

profiler = Profiler()
