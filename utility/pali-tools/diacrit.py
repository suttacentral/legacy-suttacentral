import csv
import aspell
import regex
import pickle
import pathlib
import argparse
from elasticsearch import Elasticsearch
from Levenshtein import ratio
from collections import Counter

es = Elasticsearch()

import sys
sys.path.insert(0, '../..')
import sc
import sc.textfunctions
from sc.tools import html
from sc.util import numericsortkey, unique
from sc.csv_loader import ScCsvDialect

from .common import process_node

argparser = argparse.ArgumentParser()

argparser.add_argument('source', type=pathlib.Path)
argparser.add_argument('-o', '--out', type=pathlib.Path, default='./out')
argparser.add_argument('-n', '--no-act', action="store_true")
argparser.add_argument('--lang-chars', type=str)
argparser.add_argument('--lang', type=str, required=True)

args = argparser.parse_args()


if not args.source.exists():
    raise FileNotFoundError('Source path does not exist')

if not args.out.exists():
    args.out.mkdir(parents=True)



speller = aspell.Speller('lang', args.lang)

lang_chars = set()
if args.lang_chars:
    lang_chars.update(args.lang_chars.lower() + args.lang_chars.upper())

cache_file = args.out / 'cache.pickle'
if cache_file.exists():
    with cache_file.open('rb') as f:
        cache = pickle.load(f)
else:
    cache = {}
if not args.lang in cache:
    cache[args.lang] = {}
if not "pi" in cache:
    cache["pi"] = {}
if not "asciify" in cache:
    cache["asciify"] = {}
    

unrecognized_words = Counter()


def asciify(text):
    _cache = cache['asciify']
    if text not in _cache:
        text = text.lower()
        _cache[text] = sc.textfunctions.asciify(text)
    return _cache[text]


def is_probably_lang(word):
    top3 = set([t[0] for t in langid.rank(word)][:3])
    if guess_langs.intersection(top3):
        return True
    return False
        

def suggest_lang(word):
    _cache = cache[args.lang]
    if not word in _cache:
        suggestions = speller.suggest(word)
        
        result = [(suggestion, r) for suggestion, r in 
            ((suggestion, ratio(word, suggestion)) for suggestion in suggestions[:3] if ' ' not in suggestion and '-' not in suggestion)
            if (r > 0.9)
            ]
        _cache[word] = result
    return _cache[word]

def suggest_pi_text(word):
    is_title = word.istitle()
    result = cache["pali_words"].get(asciify(word), [])
    if is_title:
        return [(w.title(), c) for w, c in result]
    else:
        return result

def suggest_pi_dict(word):
    _cache = cache["pi"]
    if word not in _cache:
        body = {
            "query": {
                "term": {
                    "term.folded": asciify(word)
                }
            }
        }
        is_title = word.istitle()
        r = es.search('en-dict', 'definition', body)
        matching_terms = [hit['_source']['term'] for hit in r['hits']['hits']]
        if is_title:
            matching_terms = (term.title() for term in matching_terms)
        matching_terms = (term for term in matching_terms if ' ' not in term)
        matching_terms = unique(matching_terms)
        result = [(term, 1) for term in matching_terms]
        _cache[word] = result
    return _cache[word]

def is_spelled_correctly(word):
    return speller.check(word)
    try:
        pass
        
    except UnicodeEncodeError:
        # This occurs when a character which cannot be represented
        # in latin-1 (or the dictionary encoding) turns up. Chances are
        # it must be an alien word.
        return False

def process_text(text):
    if not text:
        return text
    
    if args.no_act:
        words = regex.findall(r'\p{alpha}+', text)
    for word in words:
        if is_spelled_correctly(word):
            continue
        else:
            unrecognized_words[word] += 1
    
def is_roman_numeral(word, _match=regex.compile(r'^m{0,4}(cm|cd|d?c{0,3})(xc|xl|l?x{0,3})(ix|iv|v?i{0,3})$').match):
    if not word:
        return False
    return _match(word) is not None

def process_node(node, process_fn=process_text):
    if node.get('id') == 'metaarea':
        return
    node.text = process_fn(node.text)
    for child in node:
        process_node(child)
    node.tail = process_fn(node.tail)

def get_all_pali_words():
    if "pali_words" not in cache:
        words = Counter()
            
        for file in (sc.text_dir / 'pi' / 'su' / 'mn').glob('**/*.html'):
            doc = html.parse(str(file))
            root = doc.getroot()
            for e in root.cssselect('#metaarea'):
                e.drop_tree()
            text = root.text_content()
            text = regex.sub(r'[\xad”’]', '', text)
            words_from_text = regex.findall(r'\p{alpha}+', text)
            words.update(words_from_text)
            words.update(word.rstrip('ṃ') for word in words_from_text if word.endswith('ṃ'))
        
        result = {}
        for word, count in words.most_common():
            asc_word = asciify(word)
            if not asc_word in result:
                result[asc_word] = ((word, count),)
            else:
                result[asc_word] = result[asc_word] + ((word, count),)
            
        cache["pali_words"] = result
    
    return cache["pali_words"]

pali_words = get_all_pali_words()

if args.source.is_dir():
    files = sorted(args.source.glob('**/*.html'), key=numericsortkey)
else:
    files = [args.source]
for file in files:
    doc = html.parse(str(file))
    root = doc.getroot()
    process_node(root)

with (args.out / 'unrecognized_words.csv').open('w', encoding='utf8') as f:
    writer = csv.writer(f, dialect=ScCsvDialect)
    writer.writerows(unrecognized_words.most_common())
    
with (args.out / 'suggestions.csv').open('w', encoding='utf8') as f:
    writer = csv.writer(f, dialect=ScCsvDialect)
    writer.writerow(('word', 'count', 'pi-dict', 'pi-text', '{}-suggest'.format(args.lang)))
    for word, count in unrecognized_words.most_common():
        lang_suggestions = ','.join('{}:{:.4}'.format(w, c) for w, c in suggest_lang(word))
        pi_dict_suggestions = ', '.join(w for w, c in suggest_pi_dict(word))
        pi_text_suggestions = ', '.join(w for w, c in suggest_pi_text(word))
        writer.writerow((word, count, pi_dict_suggestions, pi_text_suggestions, lang_suggestions))
        
with cache_file.open('wb') as f:
    pickle.dump(cache, f, protocol=pickle.HIGHEST_PROTOCOL)
