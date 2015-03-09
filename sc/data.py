import cherrypy

import sc.scimm
import sc.search.query

class Data:
    def translation_count(self, lang, **kwargs):
        return sc.search.query.div_translation_count(lang)

    def langs(self, **kwargs):
        imm = sc.scimm.imm()
        result = {lang.uid: {'root': 1 if lang.isroot else 0,
                             'name': lang.name}
                    for lang
                    in imm.languages.values()}
        
        return result
            

            
data = Data()
