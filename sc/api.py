import json
import regex
import cherrypy

from collections import OrderedDict

import sc.scimm
from sc.util import humansortkey

utf8_json_encoder = json.JSONEncoder(ensure_ascii=False, indent=2)

def json_handler(*args, **kwargs):
    value = cherrypy.serving.request._json_inner_handler(*args, **kwargs)
    for chunk in utf8_json_encoder.iterencode(value):
        yield chunk.encode('utf8')

class API:
    @property
    def tim(self):
        import sc.textdata
        return sc.textdata.tim()
    
    @property
    def imm(self):
        import sc.scimm
        return sc.scimm.imm()
    
    @property
    def forest(self):
        import sc.forest
        return sc.forest
    
    @cherrypy.expose
    @cherrypy.tools.allow(methods=['GET'])
    @cherrypy.tools.json_out(handler=json_handler)
    def menu(self):
        def to_json(thing):
            out = OrderedDict()
            
            if hasattr(thing, "uid"):
                out.update((
                    ("uid", thing.uid),
                    ("type", type(thing).__name__.lower())
                    ("name", thing.name),
                ))
            else:
                for name in {'pitaka', 'lang', 'sect'}:
                    if hasattr(thing, name):
                        out.update(to_json(getattr(thing, name)))
                        break

            if isinstance(thing, list):
                children = [to_json(child) for child in thing]
                out["children"] = children

            
            return out
        
        return to_json(sc.menu.get_menu())
    
    @cherrypy.expose
    @cherrypy.tools.allow(methods=['GET'])
    def text(self, lang, uid):
        relative_path = self.imm.text_path(uid, lang)
        if not relative_path:
            raise cherrypy.NotFound()
        path = sc.text_dir / relative_path
        if path.exists:
            with path.open('r', encoding='utf-8') as f:
                return f.read()
        else:
            return {"error": "not found"}
    
    @cherrypy.expose
    @cherrypy.tools.allow(methods=['GET'])
    @cherrypy.tools.json_out(handler=json_handler)
    @cherrypy.tools.validate_etags()
    def uid(self, *uids, subtree_hash=None):
        result = self.forest.api.uids(*uids)
        
        
        if result:
            return result
        else:
            return {"error": "not found"}
