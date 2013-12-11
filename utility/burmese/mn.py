#!/usr/bin/env python

"""Convert pass3/mn*.html to output/mn*.html."""

import bs4
import os
import pathlib
import regex
import textwrap
import unicodedata

division = 'မဇ္ဈိမနိကာယ်'
base_dir = pathlib.Path('.')
input_dir = base_dir.join('pass3')
output_dir = base_dir.join('output', 'mn')

template = """\
<!DOCTYPE html>
<html lang="my"><head><meta charset="UTF-8"><title>{title}</title></head><body>
<div id="text" lang="my"><div id="toc"></div><section class="sutta"><article>
<hgroup><h2>{division}</h2><h1>{title}</h1></hgroup>
{content}
</article></section></div></body></html>
"""

def clean(text):
    return regex.sub(r'\s+', ' ', text.strip())

def tagit(tag, text):
    text = clean(text)
    text = textwrap.fill(text, width=78)
    if '\n' in text:
        text = '\n' + textwrap.indent(text, '  ') + '\n'
    return '<{0}>{1}</{0}>\n'.format(tag, text)

def to_sections(path):
    doc = bs4.BeautifulSoup(path.open('r', encoding='utf-8'))
    sections = []
    section = None
    for el in doc.body:
        if el.name == 'h4':
            if '-' in el.text:
                if section:
                    sections.append(section)
                section = {
                    'title': clean(el.text),
                    'content': '',
                }
            elif section:
                section['content'] += tagit('h2', el.text)
        elif section and el.name == 'p':
            section['content'] += tagit('p', el.text)
    if section:
        sections.append(section)
    return sections

if not output_dir.exists():
    os.makedirs(str(output_dir))

for input_path in input_dir.glob('mn*.html'):
    sections = to_sections(input_path)
    nums = input_path.name.replace('mn', '').replace('.html', '')
    first, last = map(int, nums.split('-'))
    if len(sections) != last + 1 - first:
        print('ERROR: Section length does not match filename: {}'.format(
            str([input_path, len(sections), last + 1 - first])))
    else:
        for i in range(first, last + 1):
            output_path = output_dir.join('mn{}.html'.format(i))
            print('Converting {} to {}'.format(input_path, output_path))
            section = sections[i - first]
            output = template.format(division=division,
                title=section['title'], content=section['content'])
            output_path.open('w', encoding='utf-8').write(output)
