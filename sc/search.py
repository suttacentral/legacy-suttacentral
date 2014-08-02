import hashlib
import json
import sc
from sc import scimm, textfunctions
from sc.util import recursive_merge, numericsortkey, grouper
import time
from urllib.request import Request

imm = scimm.imm()

searchstrings = [(t[0].uid, t[2].lstrip()) for t in imm.searchstrings]

from elasticsearch import Elasticsearch
import time
es = Elasticsearch()

from collections import defaultdict
from copy import deepcopy
from elasticsearch.helpers import bulk, streaming_bulk

def data_stream():
    for i, data in enumerate(imm.generate_search_data()):
        print(data['uid'], end=" " if i % 10 != 0 else "\n")
        yield {
            '_index': 'suttas',
            '_type': 'sutta',
            '_id': '/' + data['uid'],
            'doc': data
            }
        
    print()

def load_indexer(*args):
    indexer_dir = sc.base_dir / 'elasticsearch' / 'indexers'
    out = {}
    for arg in args:
        file = (indexer_dir / arg).with_suffix('.json')
        try:
            f = file.open('r', encoding='utf8')
            config = json.load(f)
        except ValueError:
            print("Error loading {!s}".format(file))
            raise
        finally:
            f.close()
            
        recursive_merge(out, config)
    return out

indexers = {
    "en": {
        "name": "en_texts",
        "config": load_indexer('default', 'english_mixin')
    },
    "pi": {
        "name": "pi_texts",
        "config": load_indexer('default', 'pali_mixin')
    },
    "vn": {
        "name": "vi_texts",
        "config": load_indexer('default', 'folding_mixin')
    },
    "de": {
        "name": "de_texts",
        "config": load_indexer('default', 'german_mixin')
    },
    "zh": {
        "name": "zh_texts",
        "config": load_indexer('default')
    }
}

def yield_docs_from_dir(langdir, index_name, size):
    langcode = langdir.stem
    files = sorted(langdir.glob('**/*.html'), key=lambda s: numericsortkey(s.stem))
    chunk = []
    chunk_size = 0
    for i, file in enumerate(files):
        with file.open('rb') as f:
            htmlbytes = f.read()
        
        uid = file.stem
        chunk_size += len(htmlbytes)
        chunk.append({
            '_index': index_name,
            '_type': 'text',
            '_id' : '/{}/{}'.format(langcode, uid),
            'uid': uid,
            'lang': langcode,
            'content': htmlbytes.decode(encoding='utf8')
            })
        if chunk_size > size:
            yield chunk
            chunk = []
            chunk_size = 0
    if chunk:
        yield chunk
    raise StopIteration    

def load_texts():
    timings = []
    for langdir in sc.text_dir.glob('*'):
        if langdir.is_dir():
            langcode = langdir.stem
            if langcode not in indexers:
                print("Don't know how to handle \"{}\", skipping".format(langcode))
                continue
            start = time.time()
            config = indexers[langcode]['config']
            name = indexers[langcode]['name']
            
            if not es.indices.exists(name):
                print('Creating index "{}"'.format(name))
                es.indices.create(name, config)
            for chunk in yield_docs_from_dir(langdir, name, size=500000):
                if not chunk:
                    continue
                
                print('Bulk loading chunk of {} docs'.format(len(chunk)))
                try:
                    res = bulk(es, (t for t in chunk if t is not None))
                except:
                    globals().update(locals())
                    raise
            
            timings.append('Loading "{}" took {}s'.format(name, time.time() - start))
    print(timings)

def load():
    es.indices.delete('_all')
    load_texts()
    
    #start=time.time()
    #bulk(es, data_stream())
    #print('Suttas took: {}'.format(time.time() - start))


def search(query, highlight=True, **kwargs):
    body = {
        "query": {
            "multi_match": {
                "type": "most_fields",
                "query": query,
                "fields": ["content", "content.folded", "content.lang"]
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
                    "matched_fields": ["content", "content.folded", "content.lang"],
                    "type": "fvh",
                    "fragment_size": 100,
                    "number_of_fragments": 3
                    }
                }
            }
    return es.search(body=body, **kwargs)
    
if __name__ == "__main__":
    load()
