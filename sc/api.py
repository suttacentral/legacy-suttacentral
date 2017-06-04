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
        forest = self.forest
        
        menu = self.forest.api.get_by_uids('menu')[0]
                
        
        def expand_entry(obj, parent=None):
            if 'children' in obj:
                children = []
                for child in obj['children']:
                    if isinstance(child, str):
                        if '*' in child:
                            subtrees = forest.api.get_by_uids_wildcard('root', child)
                            if subtrees:
                                for subtree in subtrees:
                                    children.append(expand_entry(subtree))
                        else:
                            subtrees = forest.api.get_by_uids('root', child)
                            if subtrees:
                                children.append(expand_entry(subtrees[0], parent=obj))
                    else:
                        children.append(expand_entry(child, parent=obj))
                obj['children'] = children
            return obj
            
        def prune(obj):
            if 'children' in obj:
                children = []
                
                for child in obj['children']:
                    if child.get('children') or (child.get('type') == 'division'):
                        children.append(child)
                        prune(child)
                
                if children:
                    obj['children'] = children
                else:
                    del obj['children']

    
        result = {'uid': 'menu', 'children': [expand_entry(child) for child in menu['data']]}
        prune(result)
        return result
    
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
    @cherrypy.tools.etags()
    def uid(self, *uids, subtree_hash=None):
        result = self.forest.api.uids(*uids)
        
        
        if result:
            return result
        else:
            return {"error": "not found"}
