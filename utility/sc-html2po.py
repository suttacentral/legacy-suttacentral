#!/usr/bin/env python

import time
import regex
import hashlib
import pathlib
import argparse
import lxml.html

def parse_args():
    parser = argparse.ArgumentParser(description='Convert HTML to PO')
    parser.add_argument('infiles', type=str, nargs='+', help="Source HTML Files")
    parser.add_argument('--out', type=str, help="Destination Folder")
    parser.add_argument('--strip-tags', type=str, help="CSS selector for stripping tags but leaving text")
    parser.add_argument('--strip-trees', type=str, help="CSS selector for removing entire element trees")
    return parser.parse_args()
    
args = parse_args()

if args.strip_tags:
    strip = args.strip
else:
    strip = '.var, .cross, .ms, q.open, q.close'

if args.strip_trees:
    remove = args.strip_trees
else:
    remove = '#metaarea'

if args.out:
    outpath = pathlib.Path(args.out)
else:
    outpath = pathlib.Path('./po-out')
if not outpath.exists():
    outpath.mkdir(parents=True)

def cleanup(element):
    for e in element.cssselect(strip):
        if not regex.search('\w', e.text_content()):
            e.drop_tree()
        else:
            e.drop_tag()
    for e in element.cssselect(remove):
        e.drop_tree()

void_tags ={'area',
            'base',
            'br',
            'col',
            'command',
            'embed',
            'hr',
            'img',
            'input',
            'keygen',
            'link',
            'meta',
            'param',
            'source',
            'track',
            'wbr'}

core_print = print
def print(*args, **kwargs):
     core_print(*args, end="")

from enum import Enum

class TokenType(Enum):
    comment = 1
    text = 2
    newline = 3
    

class Token:
    def __init__(self, type, value):
        self.type = type
        self.value = value
    
    def __repr__(self):
        return 'Token(TokenType.{}, "{}")'.format(self.type.name, self.value)

class Html2Po:
    def __init__(self):
        self.reset()
    
    def reset(self):
        self.mangle_dict = {}
        self.mangle_lookup = {}
        self.token_stream = []
    
    def make_open_tag(self, e):
        attribs = ' '.join('{}="{}"'.format(k, v)
                            for k, v 
                            in sorted(e.attrib.items()))
        
        return '<{}{}{}>'.format(e.tag,
                                 ' ' if attribs else '',
                                 attribs)

    def make_close_tag(self, e):
        return '</{}>'.format(e.tag)

    def mangle_repl(self, m):
        if m[0] in self.mangle_lookup:
            mangle_key = self.mangle_lookup[m[0]]
        else:
            mangle_key = 'MANG{}GLE'.format(len(self.mangle_dict))
            self.mangle_lookup[m[0]] = mangle_key
            self.mangle_dict[mangle_key] = m[0]
        return mangle_key

    def demangle_repl(self, m):
        return self.mangle_dict[m[0]]

    def mangle(self, html_string):
        return regex.sub('<[^<]+>', self.mangle_repl, html_string)

    def demangle(self, html_string):
        return regex.sub(r'MANG[0-9]+GLE', self.demangle_repl, html_string)

    def segment_inner(self, e):
        html_string = lxml.html.tostring(e, encoding='unicode').strip().replace('\n', ' ')
        m = regex.match(r'<[^<]+>\s*(.*)</\w+>', html_string, flags=regex.DOTALL)
        if not m:
            print(m)
            raise ValueError(html_string)
            
        html_string = m[1]
        m = regex.match(r'(?i)((?:<a[^<]*></a>\s*)*)(.*)', html_string)
        if m[1]:
            self.add_token(TokenType.comment, m[1])
            html_string = m[2]
        html_string = self.mangle(html_string)
        pattern = r'(?<!\d+)([.;:!?—]\s*)'
        parts = regex.split(pattern, html_string)
        segments = [''.join(parts[i:i+2]).strip() for i in range(0, len(parts), 2)]
        for segment in segments:
            if not segment:
                continue
            segment = self.demangle(segment)
            lines = regex.split('(<br[^>]*>)', segment)
            for i in range(0, len(lines), 2):
                line = lines[i].strip()
                if line:
                    self.add_token(TokenType.text, line)
                
                if i + 1 < len(lines):
                    br = lines[i + 1].strip()
                    if br:
                        self.add_token(TokenType.comment, br)
                self.add_token(TokenType.newline)
    
    def add_token(self, type, value=None):
        self.token_stream.append(Token(type, value))
    
    def recursive_deconstruct(self, element):
        self.add_token(TokenType.comment, self.make_open_tag(element))
        if element.tag in {'p', 'h1', 'h2', 'h3', 'h4'}:
            self.segment_inner(element)
        else:
            for child in element:
                self.recursive_deconstruct(child)
        
        if element not in void_tags:
            self.add_token(TokenType.comment, self.make_close_tag(element))
        
    def preamble(self):
        return r'''# sujato <sujato@gmail.com>, 2015.
msgid ""
msgstr ""
"Project-Id-Version: PACKAGE VERSION\n"
"Report-Msgid-Bugs-To: \n"
"POT-Creation-Date: {}\n"
"Last-Translator: sujato <sujato@gmail.com>\n"
"Language-Team: suttacentral\n"
"Language: en_GB\n"
"MIME-Version: 1.0\n"
"Content-Type: text/plain; charset=UTF-8\n"
"Content-Transfer-Encoding: 8bit\n"
"Plural-Forms: nplurals=2; plural=(n != 1);\n"
"X-Generator: sc-html2po\n"'''.format(time.strftime('%Y-%m-%d %H:%M%z'))
    
    def pretty_string(self, string):
        string = regex.sub(r'(?i)\n(\n#: <br[^>]*>)', r'\1', string)
        string = regex.sub(r'\n(\n(?:#: </\w+>(?:\n|$))+)', r'\1\n', string)
        return string
        
    
    def tostring(self):
        parts = [self.preamble()]
        last_token = None
        for token in self.token_stream:
            if token.type == TokenType.comment:
                if last_token and (last_token.type == TokenType.comment):
                    parts[-1] += token.value.strip()
                else:
                    parts.append('#: {}'.format(token.value.strip()))
            elif token.type == TokenType.text:
                parts.append('msgid "{}"'.format(token.value.strip().replace('\n', ' ')))
                parts.append('msgstr ""')
            elif token.type == TokenType.newline:
                parts.append('')
            else:
                raise ValueError('{} is not a valid type'.format(token.type))
            last_token = token
        return ('\n'.join(parts))
    
    def process(self, filename):        
        doc = lxml.html.parse(filename)
        root = doc.getroot()
        cleanup(root)
        self.root = root
        self.recursive_deconstruct(root)

for file in args.infiles:
    html2po = Html2Po()
    html2po.process(file)
    string = html2po.tostring()
    outfile = outpath / pathlib.Path(file).with_suffix('.po').name
    print(string)
    with outfile.open('w', encoding='utf8') as f:
        f.write(string)

