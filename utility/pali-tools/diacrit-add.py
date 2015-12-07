import csv
import regex
import pathlib
import argparse

import sys
sys.path.insert(0, '../..')

import sc
from sc.util import numericsortkey
from sc.tools import html
from sc.csv_loader import ScCsvDialect

from common import process_node, process_text_sub, word_rex
from hyphenate import hyphenate

argparser = argparse.ArgumentParser()
argparser.add_argument('mapping', type=pathlib.Path)
argparser.add_argument('source', type=pathlib.Path)
argparser.add_argument('-o', '--out', type=pathlib.Path, default='./out')
argparser.add_argument('-n', '--no-act', default=False, action="store_true")
argparser.add_argument('-p', '--hyphenate', type=int)


args = argparser.parse_args()

if not args.mapping.exists() or args.mapping.suffix.lower() != '.csv':
    raise ValueError('Mapping must exist and be a .csv file')

mapping = {}

with args.mapping.open('r', encoding='utf8') as f:
    for line in csv.reader(f, dialect=ScCsvDialect):
        if not line or not line[0]:
            continue
        original = line[0]
        replacement = line[2]
        if not replacement:
            continue
        if args.hyphenate:
            replacement = hyphenate(replacement, args.hyphenate)
        mapping[original] = replacement

def replace_word_from_mapping(m):
    word = m[0]
    if not args.no_act and word in mapping:
        return mapping[word]
    return word

def process_text(text):
    if not text:
        return text
    return word_rex.sub(replace_word_from_mapping, text)    

if args.source.is_dir():
    files = sorted(args.source.glob('**/*.html'), key=numericsortkey)
else:
    files = [args.source]
for file in files:
    doc = html.parse(str(file))
    root = doc.getroot()
    process_node(root, process_text)
    if not args.no_act:
        doc.write(str(file), method='html', encoding='utf8')
    
    
