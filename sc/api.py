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
    
    @cherrypy.expose
    @cherrypy.tools.allow(methods=['GET'])
    @cherrypy.tools.json_out(handler=json_handler)
    def available_texts(self, lang, prefix):
        tim = self.tim
        
        results = tim.get(lang_uid=lang)
        rex = regex.compile(prefix + '($|[^a-zA-Z])')
        
        filtered_results = {k:v for k,v in results.items() if rex.match(k)}
        
        out = []
        
        for k in sorted(filtered_results.keys(), key=humansortkey):
            v = filtered_results[k]
            out.append(OrderedDict([
                ("uid", v.uid),
                ("name", v.name),
                ("lang", v.lang),
                ("author", v.author),
            ]))
        
        return out
    
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
            raise cherrypy.NotFound()
    
    @cherrypy.expose
    @cherrypy.tools.allow(methods=['GET'])
    @cherrypy.tools.json_out(handler=json_handler)
    def languages(self):
        return [
            OrderedDict((
                ("uid", language.uid),
                ("iso_code", language.iso_code),
                ("is_root", bool(language.is_root)),
                ("name", language.name),
                ("children", [division.uid for division in language.divisions]),
            ))
            for language in self.imm.languages
        ]
                
    
    @cherrypy.expose
    @cherrypy.tools.allow(methods=['GET'])
    @cherrypy.tools.json_out(handler=json_handler)
    def query(self, uid, tr_lang=None):
        
        imm = self.imm
        
        root_lang = imm.get_root_lang_from_uid(uid)
        
        if uid in imm.divisions:
            out = self.division(uid)
        elif uid in imm.subdivisions:
            out = self.subdivision(uid)
        elif uid in imm.suttas:
            out = self.sutta(uid)
        else:
            raise cherrypy.NotFound()
        
        out["root_lang"] = root_lang
        
        self.add_text_refs(out, root_lang, tr_lang)
        return out
        
        
    def add_text_refs(self, obj, root_lang, tr_lang=None):
        if "uid" in obj:
            uid = obj["uid"]
            root_ref = self.imm.get_text_ref(uid, root_lang)
            if root_ref:
                obj["root_ref"] = OrderedDict((
                    ("name", root_ref.name),
                    ("author", root_ref.abstract),
                    ("url", root_ref.url),
                ))
            if tr_lang:
                tr_ref = self.imm.get_text_ref(uid, tr_lang)
                if tr_ref:
                    obj["tr_ref"] = OrderedDict((
                        ("name", tr_ref.name),
                        ("author", tr_ref.abstract),
                        ("url", tr_ref.url),
                    ))
            
        if "children" in obj:
            self.add_text_refs(obj["children"], root_lang, tr_lang)
                
    def division(self, uid):
        division = self.imm.divisions[uid]
        out = OrderedDict((
            ("uid", uid),
            ("type", "division"),
            ("name", division.name),
            ("parents", [division.collection.pitaka.uid, division.collection.lang.uid])
        ))
        
        children = [self.subdivision(subdivision.uid) for subdivision in division.subdivisions]
        if division.uid == division.subdivisions[0].uid:
            children = children[0]["children"]
        out["children"] = children
        return out
    
    def subdivision(self, uid):
        subdivision = self.imm.subdivisions[uid]
        return OrderedDict((
            ("uid", uid),
            ("type", "subdivision"),
            ("name", subdivision.name),
            ("children", [
                OrderedDict((
                    ("type", "vagga"),
                    ("name", vagga.name),
                    ("children", [
                        self.sutta(sutta.uid)
                        for sutta in vagga.suttas
                    ]),
                ))
                for vagga in subdivision.vaggas
            ]),
        ))
        
    def sutta(self, uid):
        sutta = self.imm.suttas[uid]
        
        return OrderedDict((
            ("uid", sutta.uid),
            ("type", "sutta"),
            ("name", sutta.name),
        ))


            
