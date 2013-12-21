#!/usr/bin/env python

"""Process Burmese Dīgha Nikāya."""

import regex
from bs4 import NavigableString

from lib import *

division = 'ဒီဃနိကာယ်'
dn16_path = pass3_dir / 'dn16.html'
dn17_path = pass3_dir / 'dn17.html'
magic_dn17_fix = 165

def process_dn(html, index):
    lines = soup_body_lines(html)
    if index == 16:
        # Attach first magic_dn17_fix lines of dn17.html onto dn16.html
        dn17_html = dn17_path.open('r', encoding='utf-8').read()
        dn17_lines = soup_body_lines(dn17_html)
        lines = list(lines) + list(dn17_lines)[:magic_dn17_fix]
    elif index == 17:
        # Remove first magic_dn17_fix lines of dn17.html
        lines = list(lines)[magic_dn17_fix:]
    title = None
    content = ''
    for el in lines:
        text = curly_quote(dash_to_em(clean(el.text)))
        if title is None:
            if text == 'ဒီဃနိကာယ်':
                # Start of vagga
                pass
            elif numbers_re.match(text[0]):
                title = text
        elif el.name in ['p', 'h2']:
            content += tagit(el.name, text)
        else:
            raise Exception('Unexpected element: {}'.format(el))
    assert title, 'No title!'
    assert content, 'No content!'
    return output_html(division=division, title=title, content=content)

if __name__ == '__main__':
    makedirs()
    for input_path in pass3_dir.glob('dn*.html'):
        index = int(regex.sub(r'[^0-9]', '', input_path.name))
        output_path = output_dn_dir / input_path.name
        print('Process: {} to {}'.format(input_path, output_path))
        with input_path.open('r', encoding='utf-8') as input:
            with output_path.open('w', encoding='utf-8') as output:
                output.write(process_dn(input.read(), index))
