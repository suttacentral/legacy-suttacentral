#!/usr/bin/env python

"""Process Burmese Saṃyutta Nikāya."""

from lib import *

division = 'သံယုတ္တနိကာယ်'
burmese_samyutta = 'သံယုတ်'
burmese_samyutta_vagga = 'တ်ပါဠိတော်'

def extract_suttas(html, subdivision_number):
    doc = soup(html)
    suttas = []
    vagga = None
    sutta = None
    number = 0
    for el in doc.body:
        if not hasattr(el, 'name'):
            continue
        name = el.name
        if name != 'h4' and name != 'p':
            continue
        text = clean(el.text)
        if text == '' or text.startswith(division) or \
                text.endswith(burmese_samyutta) or \
                text.endswith(burmese_samyutta_vagga) or \
                text.startswith(burmese_translation) or \
                text.startswith(burmese_namo_tassa):
            # print('pass')
            # print(repr(text))
            pass
        elif text.endswith(burmese_vagga):
            # print('vagga')
            # print(repr(text))
            vagga = dash_to_em(text)
        elif text.endswith(burmese_sutta):
            # print('newsutta')
            # print(repr(text))
            if sutta:
                suttas.append(sutta)
            burmese_subdivision_number = burmize_number(subdivision_number)
            number += 1
            sutta_division = '{}—{}'.format(division, burmese_subdivision_number)
            sutta = {
                'division': sutta_division,
                'vagga': vagga,
                'title': dash_to_em(text),
                'number': number,
                'content': '',
            }
        else:
            # print('content')
            # print(repr(text))
            tag = 'h2' if el.name == 'h4' else 'p'
            text = dash_to_em(curly_quote(text))
            sutta['content'] += tagit(tag, text)
    if sutta:
        suttas.append(sutta)
    return suttas

if __name__ == '__main__':
    makedirs()
    for input_path in pass3_dir.glob('sn*.html'):
        subdivision_number = int(regex.sub(r'[^0-9]', '', input_path.name))
        with input_path.open('r', encoding='utf-8') as input:
            suttas = extract_suttas(input.read(), subdivision_number)
        for sutta in suttas:
            output_filename = 'sn{}.{}.html'.format(subdivision_number,
                sutta['number'])
            output_path = output_sn_dir / output_filename
            print('Process: {} to {}'.format(input_path, output_path))
            with output_path.open('w', encoding='utf-8') as output:
                html = output_template.format(division=sutta['division'],
                    vagga=sutta['vagga'], title=sutta['title'],
                    content=sutta['content'])
                output.write(html)
