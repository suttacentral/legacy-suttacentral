import time
import json
import regex
import logging
import elasticsearch.helpers
import sc
import sc.tools.html
import sc.textfunctions

es = sc.search.es

logger = logging.getLogger(__name__)

class DictIndexer(sc.search.BaseIndexer):
    source_dir = sc.data_dir / 'dicts'
    doc_type = 'definition'
    def update(self, force=False):
        for lang_dir in self.source_dir.glob('*'):
            if lang_dir.is_dir():
                self.index_folder(lang_dir, force)

    def yield_chunks(self, entries, size=100000):
        chunk = []
        chunk_size = 0
        for i, entry in enumerate(entries):
            chunk_size += len(str(entry))
            chunk.append({
                "_id": entry["term"],
                "_source": entry
                })
            if chunk_size > size:
                yield chunk
                chunk = []
                chunk_size = 0
        if chunk:
            yield chunk
        raise StopIteration
    
    def index_folder(self, lang_dir, force):
        index_name = lang_dir.stem
        self.register_index(index_name)
        if force:
            self.es.delete_by_query(index_name, doc_type=self.doc_type, body={'query': {'match_all': {}}})
            
        if not self.es.indices.exists(index_name):
            config = sc.search.load_index_config(index_name)
            self.es.indices.create(index_name, config)

        current_mtimes = [int(file.stat().st_mtime) for file in sorted(lang_dir.iterdir()) if file.suffix in {'.html', '.json'}]
        if not force:            
            try:
                resp = self.es.get(index_name, doc_type='meta', id="dicts")
                stored_mtimes = resp['_source']['mtimes']
            except elasticsearch.exceptions.NotFoundError:
                stored_mtimes = []

            if current_mtimes == stored_mtimes:
                return
        
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

        for chunk in self.yield_chunks(sorted_entries):
            res = elasticsearch.helpers.bulk(self.es,
                        index=index_name,
                        doc_type=self.doc_type,
                        actions=chunk)

        # Success! (Or atleast we got this far)

        self.es.index(index_name, doc_type='meta', id="dicts", body={"mtimes": current_mtimes})

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

    

def get_entry(term, lang='en'):
    out = {}
    try:
        resp = es.get(index=lang, doc_type='definition', id=term)
    except:
        return None
    source = resp['_source']
    source['entries'].sort(key=lambda d: d['priority'])
    return source

def get_nearby_terms(number, lang='en'):
    resp = es.search(index=lang, doc_type='definition', _source=['term', 'gloss'], body={
      "query":{
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
    }, size=12)
    return [d['_source'] for d in resp['hits']['hits']]

def get_fuzzy_terms(term, lang='en'):
    resp = es.search(index=lang, doc_type='definition', _source=['term', 'gloss'], body={
        "query": {
            "fuzzy_like_this": {
                "fields": ["term", "term.folded"],
                "like_text": term
            }
        }
    })
    return [d['_source'] for d in resp['hits']['hits'] if d['_source']['term'] != term]

indexer = DictIndexer()

def periodic_update(i):
    if not sc.search.is_available():
        logger.error('Elasticsearch Not Available')
        return
    indexer.update()
