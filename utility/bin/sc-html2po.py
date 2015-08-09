#!/usr/bin/env python

import os
import time
import regex
import hashlib
import pathlib
import argparse
import lxml.html

def parse_args():
    parser = argparse.ArgumentParser(description='Convert HTML to PO',
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('-f', '--flat', action='store_true', help="Don't use relative paths")
    parser.add_argument('-z', '--no-zfill', action='store_true', help="Don't zfill numbers")
    parser.add_argument('--out', type=str, help="Destination Folder")
    parser.add_argument('--strip-tags',
                        type=str,
                        help="CSS selector for stripping tags but leaving text",
                        default=".ms, .msdiv")
    parser.add_argument('--strip-trees',
                        type=str,
                        help="CSS selector for removing entire element trees",
                        default="#metaarea")
    parser.add_argument('infiles', type=str, nargs='+', help="Source HTML Files")
    return parser.parse_args()
    
args = parse_args()

strip = args.strip_tags
remove = args.strip_trees
infiles = []
for infile in args.infiles:
    infile = pathlib.Path(infile)
    if infile.is_dir():
        infiles.extend(infile.glob('**/*.html'))
    else:
        infiles.append(infile)

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

from enum import Enum

class TokenType(Enum):
    comment = 1
    text = 2
    newline = 3
    end = 9
    

class Token:
    def __init__(self, type, value, ctxt=None):
        self.type = type
        self.value = value
        self.ctxt = ctxt
    
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
        html_string = lxml.html.tostring(e, encoding='unicode').strip()
        html_string = html_string.replace('\n', ' ').replace('\xad', '').replace('\xa0', ' ')
        m = regex.match(r'<[^<]+>\s*(.*)</\w+>', html_string, flags=regex.DOTALL)
        if not m:
            raise ValueError(html_string)
            
        html_string = m[1]
        m = regex.match(r'(?i)((?:<a[^<]*></a>\s*)*)(.*)', html_string)
        if m[1]:
            self.add_token(TokenType.comment, m[1])
            html_string = m[2]
        html_string = self.mangle(html_string)
        pattern = r'(?<!\d+)([.;:!?—][\u200b\s]*)'
        parts = regex.split(pattern, html_string)
        segments = [''.join(parts[i:i+2]).strip() for i in range(0, len(parts), 2)]
        sentence_count = 0
        for segment in segments:
            if not segment:
                continue
            segment = self.demangle(segment)
            lines = regex.split('(<br[^>]*>)', segment)
            for i in range(0, len(lines), 2):
                line = lines[i].strip()
                if line:
                    m = regex.match(r'^\s*(</\w+>)(.*)', line, flags=regex.DOTALL)
                    if m:
                        if self.token_stream[-1].type == TokenType.newline and self.token_stream[-2].type == TokenType.text:
                            self.token_stream[-2].value += m[1]
                            line = m[2].strip()
                    sentence_count += 1
                    ctxt = '{}:{}.{}'.format(self.uid, self.paragraph_count, sentence_count)
                    self.add_token(TokenType.text, line, ctxt)
                
                if i + 1 < len(lines):
                    br = lines[i + 1].strip()
                    if br:
                        self.add_token(TokenType.comment, br)
                self.add_token(TokenType.newline)
    
    def add_token(self, type, value=None, ctxt=None):
        self.token_stream.append(Token(type, value, ctxt))
    
    def recursive_deconstruct(self, element):
        
        self.add_token(TokenType.comment, self.make_open_tag(element))
        if element.tag in {'p', 'h1', 'h2', 'h3', 'h4'}:
            self.paragraph_count += 1
            self.segment_inner(element)
        else:
            for child in element:
                self.recursive_deconstruct(child)
        
        if element.tag not in void_tags:
            self.add_token(TokenType.comment, self.make_close_tag(element))
            if element.tag == 'html':
                self.add_token(TokenType.end)
        
    def preamble(self):
        return r'''# sujato <sujato@gmail.com>, 2015.
msgid ""
msgstr ""
"Project-Id-Version: PACKAGE VERSION\n"
"Report-Msgid-Bugs-To: \n"
"POT-Creation-Date: {}\n"
"Last-Translator: sujato <sujato@gmail.com>\n"
"Language-Team: suttacentral\n"
"Language: pi\n"
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
                if token.ctxt:
                    parts.append('msgctxt "{}"'.format(token.ctxt))
                parts.append('msgid "{}"'.format(token.value.strip().replace('\n', ' ')))
                parts.append('msgstr ""')
            elif token.type == TokenType.newline:
                parts.append('')
            elif token.type == TokenType.end:
                parts.append('')
                break
            else:
                raise ValueError('{} is not a valid type'.format(token.type))
            last_token = token
        return ('\n'.join(parts))
    
    def process(self, filename):        
        doc = lxml.html.parse(filename)
        root = doc.getroot()
        cleanup(root)
        self.root = root
        self.paragraph_count = 0
        self.uid = pathlib.Path(filename).stem
        self.recursive_deconstruct(root)

common_path = None
if not args.flat and len(infiles) > 0:
    common_path = pathlib.Path(os.path.commonprefix([str(p) for p in infiles]))

class ZFiller:
    def __init__(self):
        self.tree = {}
        self.seen = set()
    
    def split(self, string):
        return [int(part) if part.isdigit() else part 
                for part
                in regex.findall(r'\p{alpha}+|\d+|[^\p{alpha}\d]+', string)]
    
    def add_files(self, files):
        for file in files:
            string = file.relative_to(common_path)
            parts = self.split(str(string))
            branch = self.tree
            for part in parts:
                if part not in branch:
                    branch[part] = {}
                branch = branch[part]
                self.seen.add(part)
    
    def zfill(self, string):
     try:
        parts = self.split(string)
        out = []
        branch = self.tree
        for part in parts:
            if isinstance(part, int):
                maxlen = len(str(max(branch.keys())))
                out.append(str(part).zfill(maxlen))
            else:
                out.append(part)
            branch = branch[part]
        return ''.join(out)
     except Exception as e:
         globals().update(locals())
         raise

if not args.no_zfill:
    z = ZFiller()
    z.add_files(infiles)

for file in infiles:
    if common_path:
        outfile = file.relative_to(common_path)
    else:
        outfile = file.stem        
        
    if not args.no_zfill:
        outfile = z.zfill(str(outfile.parent / outfile.stem))
    outfile = outpath / (str(outfile) + '.po')
    try:
        outfile.parent.mkdir(parents=True)
    except FileExistsError:
        pass
    
    html2po = Html2Po()
    html2po.process(str(file))
    string = html2po.tostring()
    with outfile.open('w', encoding='utf8') as f:
        f.write(string)

