import time
import json
import regex
import logging
import sqlite3
import threading
import elasticsearch

import sc
import sc.tools.html
import sc.textfunctions
from sc.search.indexer import ElasticIndexer

es = sc.search.es

logger = logging.getLogger('search.dicts')

source_dir = sc.data_dir / 'dicts'

class DictIndexer(ElasticIndexer):
    doc_type = 'definition'
    lang_dir = None

    def __init__(self, config_name, lang_dir):
        self.lang_dir = lang_dir
        super().__init__(config_name=config_name,
                         index_alias=config_name + '-dict')

    def get_extra_state(self):
        current_mtimes = [int(file.stat().st_mtime)
                          for file
                          in sorted(self.lang_dir.iterdir())
                          if file.suffix in {'.html', '.json'}]
        return {'mtimes': current_mtimes,
                'version': 3}

    def is_update_needed(self):
        if not self.index_exists():
            return True
        if not self.alias_exists():
            return True
        return False
    
    def index_folder(self):
        lang_dir = self.lang_dir
        glossfile = lang_dir / 'gloss.json'

        if glossfile.exists():
            with glossfile.open('r', encoding='utf8') as f:
                glosses = {t[0]: t[1] for t in json.load(f)}
        else:
            glosses = {}
        
        all_entries = {}
        
        for source_file in lang_dir.glob('*.html'):
            self.add_file(source_file, all_entries, glosses)

        # Sort entries internally by source
        for entry in all_entries.values():
            entry["entries"].sort(key=lambda d: d["priority"])
            entry["boost"] = self.length_boost(len(entry["content"]))
        # Sort entries overall alphabetically (pali)
        sorted_entries = sorted(all_entries.values(), key=lambda d: sc.textfunctions.palisortkey(d["term"]))
        del all_entries
        
        # Correctly number entries
        for i, entry in enumerate(sorted_entries):
            entry["number"] = i + 1
        print('##### {} entries'.format(len(sorted_entries)))

        self.process_actions({'_id': entry['term'], '_source': entry}
                              for entry in sorted_entries)
    
    def fix_term(self, term):
        return regex.sub(r'[^\p{alpha}\s]', '', term).strip().casefold()
    
    def add_file(self, file, all_entries, glosses):
        root = sc.tools.html.parse(str(file)).getroot()
        meta = (('source', 'source'), ('priority', 'priority'), ('root_lang', 'lang'))
        for name, local_name in meta:
            try:
                locals()[local_name] = root.head.select('[name="{}"]'.format(name))[0].get("content")
            except IndexError:
                raise ValueError("Meta field '{}' missing in '{!s}'".format(name, file))
        source = root.head.select('[name=source]')[0].get("content")
        priority = int(root.head.select('[name=priority]')[0].get("content"))
        lang = root.head.select('[name=root_lang]')[0].get("content")
        for i, entry in enumerate(root.iter('dl')):
            term = self.fix_term(next(entry.iter('dfn')).text_content())
            
            entry.attrib['id'] = source

            # Rewrite URL's
            for a in entry.iter('a'):
                href = a.get('href')
                if not href or not href.startswith('#'):
                    continue
                a.set('href', './{}#{}'.format(href.lstrip('#'), source))
            
            if term not in all_entries:
                all_entries[term] = {
                    "term": term,
                    "lang": lang,
                    "gloss": glosses.get(term),
                    "content": '',
                    "boost": 1,
                    "number": -1,
                    "alt_terms": [],
                    "entries" : []
                }
            json_entry = all_entries[term]
            for dt in entry.iter('dt'):
                dt_text = self.fix_term(dt.text_content())
                if dt_text != term:
                    if dt_text not in json_entry["alt_terms"]:
                        json_entry["alt_terms"].append(dt_text)
            json_entry["entries"].append(
                {"source": source,
                "priority": priority,
                "html_content": str(entry)})
            content = '\n' + entry.text_content().replace('\n', ' ').replace('  ', ' ')
            json_entry["content"] += content
            
            
        logger.info('Added {} entries from {}'.format(i + 1, source))

    def update_data(self):
        self.index_folder()
    
def update():
    for lang_dir in source_dir.glob('*'):
        if lang_dir.is_dir():
            config_name = lang_dir.stem
            indexer = DictIndexer(config_name, lang_dir)
            indexer.update()

def get_entry(term, lang='en'):
    out = {}
    try:
        resp = es.get(index=lang+'-dict', doc_type='definition', id=term)
    except:
        return None
    source = resp['_source']
    source['entries'].sort(key=lambda d: d['priority'])
    return source

def nearby_terms_query(number, lang='en'):
    return {
      "size": 12,
      "_source": ['term', 'gloss'],
      "query": {
         "constant_score": {
           "filter": {
             "range": {
               "number": {
                 "gte": number - 5,
                 "lte": number + 5
               }
             }
           }
         }
      }
    }

def fuzzy_terms_query(term, lang='en'):
    return {
        "size": 10,
        "_source": ['term', 'gloss'],
        "query": {
            "multi_match": {
                "fields": ["term", "term.folded"],
                "query": term,
                "fuzziness": "AUTO"
            }
        }
    }

def get_nearby_and_fuzzy_terms(term, number, lang='en'):
    body = [
        {},
        nearby_terms_query(number, lang),
        {},
        fuzzy_terms_query(term, lang)
    ]
    
    resp = es.msearch(index=lang+'-dict',
                      doc_type='definition',
                      body=body)
    return {"nearby": [d['_source'] for d in resp['responses'][0]['hits']['hits']],
            "fuzzy": [d['_source'] for d in resp['responses'][1]['hits']['hits']]}

def get_fuzzy_terms(term, lang='en'):
    resp = es.search(index=lang+'-dict', doc_type='definition', body=fuzzy_terms_query(term, lang))
    return [d['_source'] for d in resp['hits']['hits']]
