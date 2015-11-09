
from collections import OrderedDict


import sc
import sc.scimm
import sc.textdata

from sc.views import ViewBase

available_language_templates = {f.stem for f in (sc.templates_dir / 'language').glob('*.html')
                                             if f.stem != 'generic'}

class LanguageView(ViewBase):
    template_name = 'language/generic'
    def __init__(self, lang, div_uid):
        print('Creating Language View')
        self.lang = lang
        self.div_uid = div_uid
        if div_uid is None:
            if lang in available_language_templates:
                self.template_name = 'language/' + lang
    
    def setup_context(self, context):
        tree = get_translation_tree(self.lang)
        if self.div_uid:
            root = tree.get_node_with_uid(self.div_uid)
            if root is None:
                raise ValueError("No translations available for {}/{}".format(self.lang, self.div_uid))
        else:
            root = tree.get_root()
        context.root = root
        context.lang = self.lang

class TranslationTreeBuilder:
    def __init__(self, lang):
        self.lang = lang
        self.imm = sc.scimm.imm()
        self.all_lang_translations = set(sc.textdata.tim().get(lang_uid=lang))
    
    def prune(self):
        while True:
            deleted = self.prune_empty_nodes(self.tree)
            if len(deleted) == 0:
                break
        self.prune_empty_values(self.tree)
    
    def prune_empty_nodes(self, node):
        delete = set()
        
        children = node["children"]
        if len(children) == 1 and not children[0].get("name"):
            children = node["children"][0]["children"]
            node["children"] = children
        if not children and not node["translations"]:
            delete.add(node["uid"])
        else:
            for child in children:
                delete.update(self.prune_empty_nodes(child))
            node["children"] = [child for child in children if child["uid"] not in delete]

        return delete
    
    def prune_empty_values(self, node):
        children = node["children"]
        for k in list(node):
            v = node[k]
            if isinstance(v, list) and len(v) == 0:
                del node[k]
            elif v is None:
                del node[k]
        for child in children:
            self.prune_empty_values(child)
    
    def add_descendent_counts(self, node=None):
        if node is None:
            node = self.tree
        count = 0
        for child in node.get("children", []):
            count += self.add_descendent_counts(child) or 0
        if count > 0:
            node["descendents"] = count
        return count + 1 # self counts as 1
    
    def build_from_imm(self):
        self.tree = self.add_node(self.imm.languages[self.lang], None)
        for collection in self.imm.collections.values():
            col = self.add_node(collection, self.tree)
            for division in collection.divisions:
                div = self.add_node(division, col)
                for subdivision in division.subdivisions:
                    subdiv = self.add_node(subdivision, div)
                    for sutta in subdivision.suttas:
                        sut = self.add_node(sutta, subdiv)
    
    def add_node(self, imm_tree_object, parent):
        if isinstance(imm_tree_object, sc.classes.SuttaCommon):
            type_name = 'sutta'
            if imm_tree_object.uid not in self.all_lang_translations:
                return None
        else:
            type_name = type(imm_tree_object).__name__.lower()
        translations = self.get_translations(imm_tree_object)
        try:
            obj = { "uid": imm_tree_object.uid,
                    "name": imm_tree_object.name,
                    "type": type_name,
                    "children": [],
                    "translations": translations
                    }
            if parent:
                parent["children"].append(obj)
            return obj
        except AttributeError as e:
            print('Unable to get name for {}'.format(imm_tree_object.uid))
            raise e
            return None

    def get_translations(self, imm_tree_object):
        translations = []
        if hasattr(imm_tree_object, 'translations'):
            for text_ref in imm_tree_object.translations:
                if text_ref.lang.uid == self.lang:
                    translations.append(self.create_translation(text_ref))
        else:
            text_ref = self.imm.get_text_ref(imm_tree_object.uid, self.lang)
            if text_ref:
                translations.append(self.create_translation(text_ref))
        return translations
    
    def create_translation(self, text_ref):
        return {
            "name": text_ref.name,
            "url": text_ref.url
        }
        
    def get_node_with_uid(self, uid):
        if uid:
            stack = [self.tree]
            i = 0
            while len(stack) > i:
                node = stack[i]
                if node["uid"] == uid:
                    return node
                stack.extend(child for child in node.get("children", []) if child["type"] != "sutta")
                i += 1
        return None
    
    def get_root(self):
        return self.tree

def get_translation_tree(lang:str):
    tree_builder = TranslationTreeBuilder(lang)
    tree_builder.build_from_imm()
    tree_builder.prune()
    tree_builder.add_descendent_counts()
    return tree_builder

                    
    
            
        
    
