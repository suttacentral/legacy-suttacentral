#!/usr/bin/env python

"""Process Burmese Saṃyutta Nikāya."""

from bs4 import Tag
from collections import defaultdict

from lib import *

from sc.scimm import numsortkey

extra_sutta_lines = [
    '၂၁-၅ဝ-ဇလာဗုဇာဒိဒါနူပကာရသုတ် သုံးဆယ်',  # sn29
    '၂၃-၁၁၂-သာရဂန္ဓာဒိဒါနူပကာရ သုတ်ကိုးဆယ်',  # sn31
]

division = 'သံယုတ္တနိကာယ်'
burmese_samyutta = 'သံယုတ်'
burmese_samyutta_vagga = 'တ်ပါဠိတော်'

def make_id_maps():
    project_dir = base_dir.resolve().parents[1]
    pi_sn_dir = project_dir / 'data' / 'text' / 'pi' / 'su' / 'sn'
    result = defaultdict(lambda: [])
    for path in pi_sn_dir.glob('sn*.html'):
        match = regex.match(r'^sn([0-9]+)\.([-0-9]+)\.html$', str(path.name))
        subdivision, suttas = match[1], match[2]
        result[int(subdivision)].append(suttas)
    return {subdivision: sorted(lst, key=numsortkey)
            for subdivision, lst in result.items()}

def parse_subdivision(path):
    return int(regex.sub(r'[^0-9]', '', path.name))

def extract_suttas(path, subdivision_number, id_map):
    lst = []
    def add_to_lst(pth):
        with pth.open('r', encoding='utf-8') as input:
            doc = soup(input.read())
            lst.extend(list(doc.body))
    add_to_lst(path)
    next_path = path.parent / 'sn{}-1.html'.format(subdivision_number)
    if next_path.exists():
        add_to_lst(next_path)
    return extract_suttas_from_list(lst, subdivision_number, id_map)

def clean_elements(lst, subdivision_number):
    for el in lst:
        if type(el) is not Tag:
            continue
        if el.name == 'hr':
            continue
        if el.name not in ['p', 'h2']:
            raise Exception('Unexpected tag {}'.format(el.name))
        text = clean(el.text)
        if text == '' or regex.match(r'^-+$', text):
            continue
        yield el, text

def extract_suttas_from_list(lst, subdivision_number, id_map):
    suttas = []
    vagga = None
    sutta = None
    index = 0
    base_number = 0
    last_number = 0
    for el, text in clean_elements(lst, subdivision_number):
        if text == '' or is_namo_tassa_line(text) or \
                         is_translation_line(text) or \
                         text == division:
            #log('IGNORE: {}'.format(text))
            pass
        elif is_sutta_line(text) or text in extra_sutta_lines:
            numbers = parse_numbers(text)
            if len(numbers) == 0 or len(numbers) > 2:
                raise(Exception(text))
            if numbers[0] < last_number:
                base_number += last_number
                last_number = 0
            last_number = numbers[0]
            sutta_number = str(base_number + last_number)
            if len(numbers) == 2:
                last_number = numbers[1]
                sutta_number += '-' + str(base_number + last_number)
            try:
                test_number = id_map[index]
            except IndexError:
                test_number = None
            if sutta_number != test_number:
                if sutta_number != test_number:
                    log(text)
                    log('Unexpected: {} != {}'.format(sutta_number, test_number))
            #log('new sutta: {}'.format(text))
            if sutta:
                suttas.append(sutta)
            burmese_subdivision_number = burmize_number(subdivision_number)
            sutta_division = '{}—{}'.format(division, burmese_subdivision_number)
            sutta = {
                'division': sutta_division,
                'vagga': vagga,
                'title': dash_to_em(text),
                'number': sutta_number,
                'content': '',
                'sutta_number': None,
            }
            print(sutta_number + '..', end='')
            index += 1
        elif text.endswith(burmese_samyutta):
            #log('PASS samyutta: {}'.format(text))
            pass
        elif text.endswith(burmese_samyutta_vagga):
            #log('PASS samyutta vagga: {}'.format(text))
            pass
        elif is_vagga_line(text):
            #log('vagga: {}'.format(text))
            vagga = dash_to_em(text)
            # hacks for subdivison 48
            if subdivision_number == 48:
                if text == '၁၂-သြဃဝဂ်' or text == '၁၇-သြဃဝဂ်':
                    base_number += 32
                    index += 3
            elif subdivision_number == 50:
                if text == '၅-သြဃဝဂ်':
                    base_number += 32
                    index += 3
                elif text == text == '၉-ဧသနာဝဂ်':
                    base_number += 22
                    index += 2
            elif subdivision_number == 51:
                if text == 'ဂ - သြဃဝဂ်':
                    base_number += 32
                    index += 3
            elif subdivision_number == 53:
                if text == '၅ - သြဃဝဂ်':
                    base_number += 32
                    index += 3
        else:
            # log('content: {}'.format(text))
            text = dash_to_em(curly_quote(text))
            sutta['content'] += tagit(el.name, text)
    if sutta:
        suttas.append(sutta)
    print()
    return suttas

if __name__ == '__main__':
    id_maps = make_id_maps()
    makedirs()
    for input_path in pass3_dir.glob('sn*.html'):
        if input_path.name.endswith('-1.html'):
            continue
        print('Processing: {}...'.format(input_path), end='')
        subdivision_number = parse_subdivision(input_path)
        suttas = extract_suttas(input_path, subdivision_number,
                                id_maps[subdivision_number])
        if len(suttas) != len(id_maps[subdivision_number]):
            log('sutta length != expected ({} != {})'.format(
                len(suttas), len(id_maps[subdivision_number])))
            if subdivision_number in [12, 45, 48, 50, 51, 53]:
                # 12 don't know what to do...
                # 45 combines Taṇhā/Tasinā on SC, but the text for Tasinā is 
                #    not to be found.
                # 48-53 has several suttas/combinations that don't map
                pass
            else:
                raise 'uh oh'
        for sutta in suttas:
            output_filename = 'sn{}.{}.html'.format(subdivision_number,
                sutta['number'])
            output_path = output_sn_dir / output_filename
            print('    {} to {}'.format(input_path.name, output_path.name))
            with output_path.open('w', encoding='utf-8') as output:
                html = output_html(division=sutta['division'],
                    vagga=sutta['vagga'], title=sutta['title'],
                    content=sutta['content'], css=True)
                output.write(html)
