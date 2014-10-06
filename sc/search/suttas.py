import hashlib
import json
import sc
from sc import scimm, textfunctions
from sc.util import recursive_merge, numericsortkey, grouper, unique
import time
import regex

import elasticsearch
from elasticsearch import Elasticsearch
es = Elasticsearch()

from sc.search import load_index_config

from collections import defaultdict
from copy import deepcopy
from elasticsearch.helpers import bulk, scan
import lxml.html

import logging
logger = logging.getLogger(__name__)

class SuttaIndexer:
    def fix_whitespace(self, string):
        """ Removes repeated whitespace.

        A newline  in the output indicates a paragraph break.

        """
        
        string = regex.sub(r'(?<!\n)\n(?!\n)', ' ', string)
        string = regex.sub(r'  +', ' ', string)
        string = regex.sub(r'\n\n+', r'\n', string)
        return string.strip()

    def extract_fields(self, sutta):
        content = 'Details for {}'.format(imm.uid_to_acro(sutta.uid))
        if sutta.name:
            content += ': ' + sutta.name
        if sutta.volpage:
            content += ', volpage = {}'.format(sutta.volpage)
        return {
            "uid": sutta.uid,
            "volpage": [sutta.volpage] + ([sutta.alt_volpage] or [])
            "division": sutta.subdivision.uid,
            "lang": sutta.lang.uid,
            "name": sutta.name,
        }
    
    def extract_fields_from_html(self, data):
        root = lxml.html.fromstring(data)
        text = root.find('body/div')
        assert(text is not None)
        metaarea = root.cssselect('#metaarea')
        author = []
        if metaarea:
            author = ' '.join(unique(e.text_content() for e in metaarea[0].cssselect('.author')))
            metaarea[0].drop_tree()

        for section in root.iter('section'):
            for sib in section.itersiblings():
                if sib.tag == 'section':
                    break
                sib.drop_tree()

        for p in root.iter('p'):
            p.tail = '\n\n' + (p.tail or '')

        hgroup = text.cssselect('.hgroup')[0]
        division = hgroup[0]
        title = hgroup[-1]
        if title == division:
            division = None
        others = hgroup[1:-1]
        hgroup.drop_tree()
        
        return {
            'content': self.fix_whitespace(text.text_content()),
            'author': author,
            'heading': {
                'title': title.text_content().strip() if title else '',
                'division': division.text_content().strip() if division is not None else '',
                'subhead': [e.text_content().strip() for e in others]
            }
        }

    def yield_docs_from_dir(self, lang_dir, size, to_add=None, to_delete=None):
        lang_uid = lang_dir.stem
        files = sorted(lang_dir.glob('**/*.html'), key=lambda s: numericsortkey(s.stem))
        chunk = []
        chunk_size = 0
        if to_delete:
            yield ({"_op_type": "delete", "_id": uid}
                for uid in to_delete)

        for i, file in enumerate(files):
            uid = file.stem
            action = {
                '_id' : uid,
                }
            if uid in to_add:
                with file.open('rb') as f:
                    htmlbytes = f.read()
                chunk_size += len(htmlbytes) + 512
                action.update({
                    'uid': uid,
                    'lang': lang_uid,
                    'mtime': int(file.stat().st_mtime)
                })
                action.update(self.extract_fields_from_html(htmlbytes))
            else:
                continue
            chunk.append(action)
            if chunk_size > size:
                yield chunk
                chunk = []
                chunk_size = 0
        if chunk:
            yield chunk
        raise StopIteration    

    def load(self, force=False):
        for lang_dir in sc.text_dir.glob('*'):
            if lang_dir.is_dir():
                self.index_folder(lang_dir, force)

    def index_name_from_uid(self, lang_uid):
        return lang_uid

    def index_folder(self, lang_dir, force=False):
        lang_uid = lang_dir.stem

        index_name = self.index_name_from_uid(lang_uid)
        if force:
            try:
                es.indices.delete(index_name)
            except:
                pass
        try:
            index_config = load_index_config(index_name)
        except:
            logger.warning('No indexer settings or invalid settings for language "{}"'.format(lang_uid))
            try:
                index_config = load_index_config('default')
            except:
                logger.warning('default config does not exist')
                raise
        
        if not es.indices.exists(index_name):
            logger.info('Creating index "{}"'.format(index_name))
            es.indices.create(index_name, index_config)
            es.index(index=index_name, id="files", doc_type="meta", body={"mtimes": {}})

        stored_mtimes = {hit["_id"]: hit["fields"]["mtime"][0] for hit in scan(es,
                index=index_name,
                doc_type="text",
                fields="mtime",
                query=None,
                size=500)}
        
        current_mtimes = {file.stem: int(file.stat().st_mtime) for file in lang_dir.glob('**/*.html')}
        
        to_delete = set(stored_mtimes).difference(current_mtimes)
        to_add = current_mtimes.copy()
        for uid, mtime in stored_mtimes.items():
            if mtime <= current_mtimes.get(uid):
                to_add.pop(uid)
        logger.info("For index {}, {} files already indexed, {} files to be added, {} files to be deleted".format(index_name,  len(stored_mtimes), len(to_add), len(to_delete)))
        for chunk in self.yield_docs_from_dir(lang_dir,  size=500000, to_add=to_add, to_delete=to_delete):
            if not chunk:
                continue
            
            try:
                res = bulk(es, index=index_name, doc_type="text", actions=(t for t in chunk if t is not None))
            except:
                globals().update(locals())
                raise

indexer = TextIndexer()

def search(query, highlight=True, **kwargs):
    body = {
        "query": {
            "query_string": {
                "default_field": "content",
                "fields": ["content", "content.folded", "content.stemmed"],
                "minimum_should_match": "60%",
                "query": query
                }
            }
        }
    if highlight:
        body["highlight"] = {
            "pre_tags": ['<strong class="highlight">'],
            "post_tags": ['</strong>'],
            "order": "score",
            "fields": {
                "content" : {
                    "matched_fields": ["content", "content.folded", "content.stemmed"],
                    "type": "fvh",
                    "fragment_size": 100,
                    "number_of_fragments": 3
                    }
                }
            }
    return es.search(body=body, **kwargs)


if __name__ == "__main__":
    pass
    #load()
