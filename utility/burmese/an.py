#!/usr/bin/env python

"""Process Burmese Aṅguttara Nikāya."""

import regex
from bs4 import Tag
from collections import defaultdict

from lib import *

# from sc.scimm import numsortkey

division = 'အင်္ဂုတ္တရနိကာယ်'

adjustments = {
    1: {
        ('၁-ရူပါဒိဝဂ်', None): ('1-10', 10),
        ('၂-နီဝရဏပ္ပဟာနဝဂ်', None): ('11-20', 20),
        ('၃-အကမ္မနိယဝဂ်', None): ('21-30', 30),
        ('၄-အဒန္တဝဂ်', None): ('31-40', 40),
        ('၅-ပဏိဟိတအစ္ဆဝဂ်', None): ('41-50', 50),
        ('၆-အစ္ဆရာသင်္ဃာတဝဂ်', None): ('51-60', 60),
        ('၇-ဝီရိယာရမ္ဘာဒိဝဂ်', None): ('61-70', 70),
        ('၈-ကလျာဏမိတ္တာဒိဝဂ်', None): ('71-80', 80),
        ('၉-ပမာဒါဒိဝဂ်', None): ('81-97', 97),
        ('၁ဝ-ဒုတိယ ပမာဒါဒိဝဂ်', None): ('98-139', 139),
        ('၁၁-အဓမ္မဝဂ်', None): ('140-149', 149),
        ('၁၂-အနာပတ္တိဝဂ်', None): ('150-169', 169),
        ('၁၃-ဧကပုဂ္ဂလဝဂ်', None): ('170-187', 187),
        ('၁၄-ဧတဒဂ္ဂဝဂ် ၁-ပဌမဝဂ်', None): ('188-197', 197),
        ('၁၄-ဧတဒဂ္ဂ္ဂဝဂ် ၂- ဒုတိယဝဂ်', None): ('198-208', 208),
        ('၁၄-ဧတဒဂ္ဂဝဂ် ၃-တတိယဝဂ်', None): ('209-218', 218),
        ('၁၄-ဧတဒဂ္ဂဝဂ် ၄-စတုတ္ထဝဂ်', None): ('219-234', 234),
        ('၁၄-ဧတဒဂ္ဂဝဂ် ၅-ပဉ္စမဝဂ်', None): ('235-247', 247),
        ('၁၄-ဧတဒဂ္ဂဝဂ် ၆-ဆဋ္ဌဝဂ်', None): ('248-257', 257),
        ('၁၄-ဧတဒဂ္ဂဝဂ် ၇-သတ္တမဝဂ်', None): ('258-267', 267),
        ('၁၅-အဋ္ဌာနပါဠိ၁-ပဌမဝဂ်', None): ('268-277', 277),
        ('၁၅-အဋ္ဌာနပါဠိ ၂-ဒုတိယဝဂ်', None): ('278-286', 286),
        ('၁၅-အဋ္ဌာနပါဠိ ၃-တတိယဝဂ်', None): ('287-295', 295),
        ('၁၆-ဧကဓမ္မပါဠိ ၁-ပဌမဝဂ်', None): ('296-305', 297),
        ('၁၆-ဧကဓမ္မပါဠိ ၂-ဒုတိယဝဂ်', None): ('306-315', 307),
        ('၁၆-ဧကဓမ္မပါဠိ ၃-တတိယဝဂ်', None): ('316-332', 332),
        ('၁၆-ဧကဓမ္မပါဠိ ၄-စတုတ္ထဝဂ်', None): ('333-377', 377),
        ('၁၇-ပသာဒကရဓမ္မဝဂ်', None): ('378-393', 393),
        ('၁၈-အပရအစ္ဆရာသင်္ဃာတဝဂ်', None): ('394-574', 574),
        ('၁၉-ကာယဂတာသတိဝဂ်', None): ('575-615', 615),
        ('၂ဝ-အမတဝဂ်', None): ('616-627', 627),
    },
    2: {
        ('၂-အဓိကရဏဝဂ်', None): ('11-20', 20),
        ('၃-ဗာလဝဂ်', None): ('21-31', 31),
        ('၄-သမစိတ္တဝဂ်', None): ('32-41', 41),
        ('၅-ပရိသဝဂ်', None): ('42-51', 51),
        ('(၆) ၁-ပုဂ္ဂလဝဂ်', None): ('52-63', 63),
        ('(၇) ၂-သုခဝဂ်', None): ('64-76', 76),
        ('(၈) ၃-သနိမိတ္တဝဂ်', None): ('77-86', 86),
        ('(၉) ၄-ဓမ္မဝဂ်', None): ('87-97', 97),
        ('(၁ဝ) ၅-ဗာလဝဂ်', None): ('98-117', 117),
        ('(၁၁) ၁-အာသာဒုပ္ပဇဟဝဂ်', None): ('118-129', 129),
        ('(၁၂) ၂-အာယာစနဝဂ်', None): ('130-140', 140),
        ('(၁၃) ၃-ဒါနဝဂ်', None): ('141-150', 150),
        ('(၁၄) ၄-သန္ထာရဝဂ်', None): ('151-162', 162),
        ('(၁၅) ၅-သမာပတ္တိဝဂ်', None): ('163-179', 179),
        ('၁-ကောဓပေယျာလ', None): ('180-229', 229),
        ('၂-အကုသလပေယျာလ', None): ('230-279', 279),
        ('၃-ဝိနယပေယျာလ', None): ('280-309', 309),
        ('၄-ရာဂပေယျာလ', None): ('310-479', 479),
    },
    3: {
        ('(၁၆) ၆-အစေလကဝဂ်', None): ('156-162', 162),
        ('(၁၇) ၇-ကမ္မပထပေယျာလ', None): ('163-182', 182),
        ('(၁၈) ၈-ရာဂပေယျာလ', None): ('183-352', 352),
    },
    5: {
        ('၂-သိက္ခာပဒပေယျာလ', '၃-ရာဂပေယျာလသုတ်'): ('303-1151', 1151),
    },
    6: {
        ('၂၄-ရာဂပေယျာလ', None): ('140-649', 649),
    },
    7: {
        ('၁ဝ-အာဟုနေယျဝဂ်', None): ('95-614', 614),
        ('၁၁-ရာဂပေယျာလ', None): ('615-1124', 1124),
    },
    8: {
        ('(၁ဝ) ၅-သာမညဝဂ်', None): ('91-117', 117),
        ('၁၁-ရာဂပေယျာလ', None): ('118-627', 627),
    },
    9: {
        ('(၈) ၃-သမ္မပ္ပဓာနဝဂ်', '၁-သိက္ခာသုတ်'): ('73-81', 81),
        ('(၉) ၄-ဣဒ္ဓိပါဒဝဂ်', '၁-သိက္ခာသုတ်'): ('83-91', 91),
        ('(၁ဝ) ၅-ရာဂပေယျာလ', None): ('93-432', 432),
    },
    10: {
        ('(၂ဝ) ၅-အပရပုဂ္ဂလဝဂ် န သေဝိတဗ္ဗာဒိသုတ်များ', None): ('199-210', 210),
        ('(၂၂) ၂-သာမညဝဂ်', None): ('221-236', 236),
        ('၂၃-ရာဂပေယျာလ', None): ('237-746', 746),
    },
    11: {
        ('၃-သာမညဝဂ်', None): ('22-981', 981),
        ('၄-ရာဂပေယျာလ', None): ('982-1151', 1151),
    }
}

def is_division_line(text):
    return text == division or text == 'အင်္ဂုတ္တိုရ်ပါဠိတော်'

def is_subdivision_line(text):
    return text.endswith('နိပါတ်')

def is_some_header_line(text):
    return text.endswith('ဏ္ဏာသက') or text.endswith('သုတ်ငါးဆယ်')

def get_files():
    buckets = defaultdict(lambda: [])
    for input_path in pass3_dir.glob('an*.html'):
        match = regex.match(r'an([0-9]+)(-[0-9])?\.html$', input_path.name)
        if match:
            sd_index = int(match[1])
        else:
            raise Exception('Unexpected filename: {}'.format(input_path))
        buckets[sd_index].append(input_path)
    return [(i, sorted(buckets[i])) for i in sorted(buckets.keys())]

def extract_elements(paths):
    elements = []
    for path in paths:
        with path.open('r', encoding='utf-8') as input:
            doc = soup(input.read())
            elements.extend(list(doc.body))
    return elements

def clean_elements(elements):
    for el in elements:
        if type(el) is not Tag or el.name == 'hr':
            continue
        if el.name not in ['p', 'h2']:
            raise Exception('Unexpected tag {}'.format(el.name))
        text = clean(el.text)
        yield el, text

def contextualize_elements(elements):
    context = None
    for el, text in clean_elements(elements):
        if text == '' or \
           is_namo_tassa_line(text) or \
           is_translation_line(text) or \
           is_division_line(text) or \
           is_subdivision_line(text) or \
           is_some_header_line(text):
            continue
        vagga_sutta = parse_vagga_sutta_line(text)
        if vagga_sutta:
            if vagga_sutta['vagga']:
                context = vagga_sutta
            else:  # only sutta
                if context:
                    # print(context['sutta_line'], vagga_sutta['sutta_line'])
                    context.update({
                        'int_sutta_number': vagga_sutta['int_sutta_number'],
                        'sutta_number': vagga_sutta['sutta_number'],
                        'sutta': vagga_sutta['sutta'],
                        'sutta_line': vagga_sutta['sutta_line'],
                    })
                else:
                    context = vagga_sutta
        elif context:
            yield context, el, text
        else:
            # print('No context yet - ignoring: {}'.format(text))
            pass

def adjust_sutta(sutta, sutta_index):
    sutta_index += 1
    key = (sutta['vagga_line'], sutta['sutta_line'])
    adjustment = adjustments.get(sd_index, {}).get(key, None)
    if adjustment:
        sutta['number'] = adjustment[0]
        sutta_index = adjustment[1]
    else:
        sutta['number'] = str(sutta_index)
        sutta_line = sutta['sutta_line']
        if sutta_line:
            numbers = parse_numbers(sutta_line)
            if len(numbers) == 1:
                pass
            elif len(numbers) == 2:
                difference = numbers[1] - numbers[0]
                number = '{}-{}'.format(sutta_index,
                                        sutta_index + difference)
                sutta['number'] = number
                sutta_index += difference
            else:
                raise Exception('Unexpected number: {}'.format(sutta_line))
    return (sutta, sutta_index)

def extract_suttas_from_elements(sd_index, elements):
    suttas = []
    sutta = None
    sutta_index = 0
    for context, el, text in contextualize_elements(elements):
        if not sutta or sutta['vagga_line'] != context['vagga_line'] or \
                        sutta['sutta_line'] != context['sutta_line']:
            if sutta:
                suttas.append(sutta)
            sutta = context.copy()
            sutta['content'] = ''
            if sutta['sutta_line']:
                sutta['title'] = sutta['sutta_line']
                sutta['vagga_title'] = sutta['vagga_line']
            else:
                sutta['title'] = sutta['vagga_line']
                sutta['vagga_title'] = None
            sutta, sutta_index = adjust_sutta(sutta, sutta_index)
        text = dash_to_em(curly_quote(text))
        sutta['content'] += tagit(el.name, text)
    if sutta:
        suttas.append(sutta)
    return suttas

if __name__ == '__main__':
    makedirs()
    for sd_index, paths in get_files():
        names = map(lambda p: p.name, paths)
        print('Parsing: {}'.format(', '.join(names)), end='')
        elements = extract_elements(paths)
        print(' ({} elements)'.format(len(elements)))
        suttas = extract_suttas_from_elements(sd_index, elements)
        for sutta in suttas:
            output_filename = 'an{}.{}.html'.format(sd_index, sutta['number'])
            output_path = output_an_dir / output_filename
            print('    -> {} ({} lines)'.format(
                output_path.name, len(sutta['content'].splitlines())))
            # print('        {}: (,),'.format(repr((sutta['vagga_line'], sutta['sutta_line']))))
            with output_path.open('w', encoding='utf-8') as output:
                html = output_html(division=division,
                    vagga=sutta['vagga_title'], title=sutta['title'],
                    content=sutta['content'])
                output.write(html)
