#!/usr/bin/env python

import time
import regex
import pathlib
import argparse
import lxml.html

def parse_args():
    parser = argparse.ArgumentParser(description='Convert HTML to PO')
    parser.add_argument('infiles', type=str, nargs='+', help="Source PO Files")
    parser.add_argument('--out', type=str, help="Destination Folder")
    return parser.parse_args()
    
args = parse_args()

if args.out:
    outpath = pathlib.Path(args.out)
else:
    outpath = pathlib.Path('./html-out')
if not outpath.exists():
    outpath.mkdir(parents=True)

class Po2Html:
    def __init__(self):
        self.parts = []
    def process(self, file):
        with open(file, 'r', encoding='utf8') as f:
            string = f.read()
        dropping = True
        last_is_comment = False
        out = [self.head()]
        for m in regex.finditer(r'#[.:]\s*(?<comment>.*)|msgstr (?:"(?<msgstr>.*)"\n?)+', string):
            print(m[0], dropping)
            if dropping:
                if m['comment']:
                    if regex.match(r'[\s\p{punct}]*VAR', m['comment']):
                        continue
                    body_m = regex.search(r'(?is)<body.*', m['comment'])
                    if body_m:
                        dropping = False
                        out.append(body_m[0])
                    
            else:
                if m['comment']:
                    out.append(m['comment'])
                    last_is_comment = True
                else:
                    passage = self.unescape(' '.join(m.captures('msgstr')))
                    passage = passage.strip()
                    if passage:
                        if not last_is_comment:
                            out.append(' ')
                        last_is_comment = False
                        out.append(passage)
                    
        html_string = ''.join(out)
        return self.pretty_print(html_string)
    
    def unescape(self, string):
        return string.replace(r'\"', '"').replace('\\\\', '\\')
    
    open_tag_newline_before = {'html','head','body','div','section',
        'article', 'hgroup', 'blockquote', 'header', 'footer', 'nav', 'menu',
        'meta', 'ul', 'ol', 'table', 'tr', 'tbody', 'thead', 'p'}
    open_tag_newline_after = open_tag_newline_before - {'p', 'li', 'td', 'html'}
    close_tag_newline_after = open_tag_newline_before
    close_tag_newline_before = open_tag_newline_after
    
    def handle_open_tag(self, m):
        out = ''
        if m[1] in self.open_tag_newline_before:
            out += '\n'
        out += m[0]
        if m[1] in self.open_tag_newline_after:
            out += '\n'
        return out
        
    def handle_close_tag(self, m):
        out = ''
        if m[1] in self.close_tag_newline_before:
            out += '\n'
        out += m[0]
        if m[1] in self.close_tag_newline_after:
            out += '\n'
        return out
    
    def pretty_print(self, string):
        string = regex.sub(r'<([a-z]+)[^>]*>', self.handle_open_tag, string)
        string = regex.sub(r'</([a-z]+)>', self.handle_close_tag, string)
        string = regex.sub(r'\s{2,}', lambda m: '\n' if '\n' in m[0] else ' ', string)
        return string.strip()
    
    def head(self):
        return '''<!DOCTYPE html>
<html>
<head>
<meta charset="utf8">
<title></title>
</head>'''

for file in args.infiles:
    po2html = Po2Html()
    string = po2html.process(file)
    
    outfile = outpath / pathlib.Path(file).with_suffix('.html').name
    with outfile.open('w', encoding='utf8') as f:
        f.write(string)

