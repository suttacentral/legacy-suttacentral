#!/usr/bin/env python

"""Create simplified HTML from original HTML found on pitakataw.com."""

from bs4 import NavigableString, Tag

from lib import *

pass1_template = """\
<!DOCTYPE html>
<html lang="my">
<head>
<meta charset="utf-8">
<title>{title}</title>
</head>
<body>
{body}</body>
</html>
"""

def pass1(text):
    dom = soup(text)
    title = dom.select('title')[0].text
    post = dom.select('.blogPost')[0]
    body = ''
    for el in post:
        if type(el) is NavigableString:
            text = el.string.strip()
            if text:
                text = text.replace('\n', ' ')
                body += tagit('p', text)
        elif 'blogger-labels' not in el.get('class', []):
            tag = el.name
            if tag == 'center':
                body += '<hr>\n'
            else:
                text = el.text.strip()
                if text:
                    text = text.replace('\n', ' ')
                    tag = el.name
                    if tag in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
                        tag = 'h2'
                    else:
                        tag = 'p'
                    body += tagit(tag, text)
    return pass1_template.format(title=title, body=body)

if __name__ == '__main__':
    makedirs()
    for input_path in originals_dir.glob('*.html'):
        output_path = pass1_dir / input_path.name.lower().replace('sn-', 'sn')
        print('Pass 1: {} -> {}'.format(input_path, output_path))
        with input_path.open('r', encoding='utf-8') as input:
            with output_path.open('w', encoding='utf-8') as output:
                output.write(pass1(input.read()))
