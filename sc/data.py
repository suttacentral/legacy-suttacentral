import cherrypy

import sc.scimm
import sc.search.query

class Data:
    def translation_count(self, lang, **kwargs):
        imm = sc.scimm.imm()
        return imm.translation_count(lang=lang)

    def langs(self, **kwargs):
        imm = sc.scimm.imm()
        result = {lang.uid: {'root': 1 if lang.isroot else 0,
                             'name': lang.name}
                    for lang
                    in imm.languages.values()}
        
        return result

    def suttas(self, suttas, **kwargs):
        uids = suttas
        result = {}
        for uid in uids.split(','):
            result[uid] = self.sutta_info(uid)
        return result

    def parallels(self, parallels, ll_lang=None, **kwargs):
        uids = parallels
        result = {}
        for uid in uids.split(','):
            ll_info = self.parallels_info(uid, ll_lang, **kwargs)
            if ll_info:
                result[uid] = ll_info
        return result
    
    def parallels_info(self, uid, ll_lang=None, **kwargs):
        imm = sc.scimm.imm()
        sutta = imm.suttas.get(uid)
        if not sutta:
            return {'error': 'sutta not found'}

        if ll_lang:
            ll_lang = set(ll_lang.split(','))

        result = {} 

        for ll in sutta.parallels:
            for tr in ll.sutta.translations:
                if ll_lang and tr.lang.uid not in ll_lang:
                    continue
                if not tr.url.startswith('http://'):
                    if not tr.lang.uid in result:
                        result[tr.lang.uid] = []
                    ll_json = self._text_ref(tr)
                    ll_json['uid'] = ll.sutta.uid
                    ll_json['acro'] = ll.sutta.acronym
                    if ll.partial:
                        ll_json['partial'] = True
                    result[tr.lang.uid].append(ll_json)
        return result
        
    def sutta_info(self, uid, lang='en', **kwargs):
        imm = sc.scimm.imm()
        sutta = imm.suttas.get(uid)
        if not sutta:
            return {'error': 'sutta not found'}

        result = {
            'uid': sutta.uid,
            'acro': sutta.acronym,
            'lang': sutta.lang.uid,
            'name': sutta.name,
            'subdivision': sutta.subdivision.name,
            'division': sutta.subdivision.division.name,
        }

        if sutta.text_ref:
            result['text_ref'] = self._text_ref(sutta.text_ref)
        translations = {}
        for tr in sutta.translations:
            if tr.url.startswith('http'):
                    continue
            if tr.lang.uid == lang:
                translations[tr.lang.uid] = self._text_ref(tr);
        if translations:
            result['translations'] = translations
        return result

    def _text_ref(self, tr):
        return {
            'lang': tr.lang.uid,
            'url': tr.url,
            'name': tr.name
        }
    
    def text_images(self, uid, volpage_ids, **kwargs):
        from sc.text_image_index import get
        out = {}
        for vp_id in volpage_ids.split(','):
            result = get(uid, vp_id)
            if result:
                out[vp_id] = {"url": '/text_images/' + result,
                              "filename": (sc.text_image_symlink_dir / result).resolve().name}
        return out

data = Data()
