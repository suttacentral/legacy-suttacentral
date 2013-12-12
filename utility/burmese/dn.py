#!/usr/bin/env python

"""Process Burmese Dīgha Nikāya."""

from lib import *

division = 'ဒီဃနိကာယ်'

def process_dn(html):
    vaggafile = False
    title = None
    content = ''
    for el in soup(html).body:
        try:
            text = el.text
        except AttributeError:
            continue
        text = clean(text)
        if title is None:
            if text == 'ဒီဃနိကာယ်':
                # Start of vagga
                vaggafile = True
            elif text and numbers_re.match(text[0]):
                title = text
            continue
        if el.name == 'h4':
            content += tagit('h2', text)
        elif el.name == 'p':
            content += tagit('p', text)
    assert title, 'No title!'
    assert content, 'No content!'
    html = output_template.format(division=division,
        title=title, content=content)
    return html

if __name__ == '__main__':
    makedirs()
    for input_path in pass3_dir.glob('dn*.html'):
        output_path = output_dn_dir / input_path.name
        print('Process: {} to {}'.format(input_path, output_path))
        with input_path.open('r', encoding='utf-8') as input:
            with output_path.open('w', encoding='utf-8') as output:
                output.write(process_dn(input.read()))
