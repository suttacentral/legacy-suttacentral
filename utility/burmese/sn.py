#!/usr/bin/env python

"""Process Burmese Saṃyutta Nikāya."""

from bs4 import Tag
from collections import defaultdict

from lib import *

from sc.scimm import numsortkey

line_fixes = {
    # SN4
    '၊ ၁-တပေါကမ္မသုတ်': '၁-တပေါကမ္မသုတ်',
    # SN15
    '-၁-တိဏကဋ္ဌသုတ်': '၁-တိဏကဋ္ဌသုတ်',
    # SN17
    '၃-သုဝဏ္ဏနိက္ခသုတ်စသော (၈) သုတ်': '၃-၁ဝ-သုဝဏ္ဏနိက္ခသုတ်စသော (၈) သုတ်',
    # SN23
    '၁-မာရာဒိသုတ္တ ဧကာဒသကသုတ်': '၁-၁၁-မာရာဒိသုတ္တ ဧကာဒသကသုတ်',
    # SN35
    '၃-ပဌမ သမုဒ္ဒသုတ်': '၁-ပဌမ သမုဒ္ဒသုတ်',
    # SN46
    '၃၁၂-၃၂၃- ပုနဂင်္ဂ ါနဒီအာဒိသုတ်': '၁-၁၂-ပုနဂင်္ဂ ါနဒီအာဒိသုတ်', 
    '၃၂၄-၃၃၃-တထာဂတာဒိသုတ်': '၁-၁ဝ-တထာဂတာဒိသုတ်',
    '၃၃၄-၃၄၅-ပုနဗလာဒိသုတ်': '၁-၁၂-ပုနဗလာဒိသုတ်',
    '၃၄၆-၃၅၆-ပုနဧသနာဒိသုတ်': '၁-၁ဝ-ပုနဧသနာဒိသုတ်',
    '၃၅၇-၃၆၆-ပုနသြဃာဒိသုတ်': '၁-၁ဝ-ပုနသြဃာဒိသုတ်',
    # SN54
    '-၅-ဒုတိယ ဖလသုတ်': '၅-ဒုတိယ ဖလသုတ်',
    '၄.ဒုတိယ အာနန္ဒသုတ်': '၄-ဒုတိယ အာနန္ဒသုတ်',
    # SN55
    '၁-ဒုတိယ အဘိသန္ဒသုတ်': '၂-ဒုတိယ အဘိသန္ဒသုတ်',
    '၁-တတိယ အဘိသန္ဒသုတ်': '၃-တတိယ အဘိသန္ဒသုတ်',
}

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

def clean_elements(lst):
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
        text = line_fixes.get(text, text)
        yield el, text

def extract_suttas_from_list(lst, subdivision_number, id_map):
    suttas = []
    vagga = None
    sutta = None
    index = 0
    base_number = 0
    last_number = 0
    for el, text in clean_elements(lst):
        if text == '' or is_namo_tassa_line(text) or \
                         is_translation_line(text) or \
                         text == division:
            #log('IGNORE: {}'.format(text))
            pass
        elif is_sutta_line(text):
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
                # # Force in this edge case...
                # if '-' not in sutta_number and '-' in test_number:
                #     test_number_1, test_number_2 = test_number.split('-')
                #     if sutta_number == test_number_1:
                #         sutta_number = test_number
                #         last_number = int(test_number_2) - base_number
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
        else:
            # log('content: {}'.format(text))
            text = dash_to_em(curly_quote(text))
            sutta['content'] += tagit(el.name, text)
    if sutta:
        suttas.append(sutta)
    print()
    return suttas

ignore_subdivisions = [
    12,  # mismatch
    24,  # mismatch
    29,  # mismatch
    31,  # mismatch
    45,  # mismatch
    47,  # mismatch
    48,  # mismatch
    49,  # mismatch
    50,  # mismatch
    51,  # mismatch
    53,  # mismatch
    56,  # mismatch
]

if __name__ == '__main__':
    id_maps = make_id_maps()
    makedirs()
    for input_path in pass3_dir.glob('sn*.html'):
        if input_path.name.endswith('-1.html'):
            continue
        print('Reading: {}...'.format(input_path), end='')
        subdivision_number = parse_subdivision(input_path)
        if subdivision_number in ignore_subdivisions:
            print('IGNORING')
            continue
        suttas = extract_suttas(input_path, subdivision_number,
                                id_maps[subdivision_number])
        assert len(suttas) == len(id_maps[subdivision_number])
        for sutta in suttas:
            output_filename = 'sn{}.{}.html'.format(subdivision_number,
                sutta['number'])
            output_path = output_sn_dir / output_filename
            print('Process: {} to {}'.format(input_path, output_path))
            with output_path.open('w', encoding='utf-8') as output:
                html = output_html(division=sutta['division'],
                    vagga=sutta['vagga'], title=sutta['title'],
                    content=sutta['content'], css=True)
                # output.write(html)
