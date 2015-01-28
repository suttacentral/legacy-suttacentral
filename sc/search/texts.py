import json
import time
import regex
import hashlib
import logging
import lxml.html
from copy import deepcopy
from collections import defaultdict
from elasticsearch.helpers import bulk, scan
import sc
from sc import scimm, textfunctions
from sc.search import load_index_config
from sc.util import recursive_merge, numericsortkey, grouper, unique

logger = logging.getLogger(__name__)
logger.setLevel('DEBUG')

handler = logging.StreamHandler()
handler.setLevel('DEBUG')
logger.addHandler(handler)


class TextIndexer(sc.search.BaseIndexer):
    htmlparser = lxml.html.HTMLParser(encoding='utf8')
    def fix_whitespace(self, string):
        """ Removes repeated whitespace.

        A newline  in the output indicates a paragraph break.

        """
        
        string = regex.sub(r'(?<!\n)\n(?!\n)', ' ', string)
        string = regex.sub(r'  +', ' ', string)
        string = regex.sub(r'\n\n+', r'\n', string)
        return string.strip()
        
    def extract_fields_from_html(self, data):
        root = lxml.html.fromstring(data, parser=self.htmlparser)
        text = root.find('body/div')
        if text is None:
            raise ValueError("Structure of html is not body > div")
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

        for e in root.cssselect('.add'):
            e.drop_tree()
        
        hgroup = text.cssselect('.hgroup')[0]
        division = hgroup[0]
        title = hgroup[-1]
        if title == division:
            division = None
        others = hgroup[1:-1]
        hgroup.drop_tree()
        content = self.fix_whitespace(text.text_content())
        
        return {
            'content': content,
            'author': author,
            'heading': {
                'title': title.text_content().strip() if title is not None else '',
                'division': division.text_content().strip() if division is not None else '',
                'subhead': [e.text_content().strip() for e in others]
            },
            'boost': self.length_boost(len(content))
        }

    def yield_docs_from_dir(self, lang_dir, size, to_add=None, to_delete=None):
        imm = sc.scimm.imm()
        lang_uid = lang_dir.stem
        files = sorted(lang_dir.glob('**/*.html'), key=lambda s: numericsortkey(s.stem))
        chunk = []
        chunk_size = 0
        if to_delete:
            yield ({"_op_type": "delete", "_id": uid}
                for uid in to_delete)

        for i, file in enumerate(files):
            try:
                uid = file.stem
                root_lang = imm.get_root_lang_from_uid(uid)
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
                        'root_lang': root_lang,
                        'is_root': lang_uid == root_lang,
                        'mtime': int(file.stat().st_mtime)
                    })
                    
                    action.update(self.extract_fields_from_html(htmlbytes))
            except (ValueError, IndexError) as e:
                logger.error("An error while processing {!s} ({!s})".format(file, e))
                continue

            chunk.append(action)
            if chunk_size > size:
                yield chunk
                chunk = []
                chunk_size = 0
                time.sleep(0.25)
        if chunk:
            yield chunk
        raise StopIteration    

    def update(self, force=False):
        for lang_dir in sc.text_dir.glob('*'):
            if lang_dir.is_dir():
                self.index_folder(lang_dir, force)

    def index_name_from_uid(self, lang_uid):
        return lang_uid

    def index_folder(self, lang_dir, force=False):
        lang_uid = lang_dir.stem

        index_name = self.index_name_from_uid(lang_uid)
        self.register_index(index_name)
        if force:
            try:
                self.es.indices.delete(index_name)
            except:
                pass
        try:
            index_config = load_index_config(index_name)
        except:
            logger.warning('No indexer settings or invalid settings for language "{}", using "default"'.format(lang_uid))
            try:
                index_config = load_index_config('default')
            except:
                logger.warning('default config does not exist')
                raise
        
        if not self.es.indices.exists(index_name):
            logger.info('Creating index "{}"'.format(index_name))
            self.es.indices.create(index_name, index_config)
            self.es.index(index=index_name, id="files", doc_type="meta", body={"mtimes": {}})
        try:
            stored_mtimes = {hit["_id"]: hit["fields"]["mtime"][0] for hit in scan(self.es,
                index=index_name,
                doc_type="text",
                fields="mtime",
                query=None,
                size=500) if 'fields' in hit}
        except Exception as e:
            logger.error('A problem occured with index {}'.format(lang_uid))
            raise
        
        current_mtimes = {file.stem: int(file.stat().st_mtime) for file in lang_dir.glob('**/*.html')}
        
        to_delete = set(stored_mtimes).difference(current_mtimes)
        to_add = current_mtimes.copy()
        for uid, mtime in stored_mtimes.items():
            if uid in to_delete:
                continue
            if mtime <= current_mtimes.get(uid):
                to_add.pop(uid)
        logger.info("For index {}, {} files already indexed, {} files to be added, {} files to be deleted".format(index_name,  len(stored_mtimes), len(to_add), len(to_delete)))
        for chunk in self.yield_docs_from_dir(lang_dir,  size=500000, to_add=to_add, to_delete=to_delete):
            if not chunk:
                continue
            
            try:
                logger.debug('Sending {} actions to es'.format(len(chunk)))
                res = bulk(self.es, index=index_name, doc_type="text", actions=(t for t in chunk if t is not None))
                print(res)
            except:
                raise

indexer = TextIndexer()

def periodic_update(i):
    if not sc.search.is_available():
        logger.error('Elasticsearch Not Available')
        return
    indexer.update()
