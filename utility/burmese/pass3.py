#!/usr/bin/env python

"""Cleanup encoding issues.

- Normalize Unicode to NFC.
- Fix encoding issues identified by Nay.

See http://stackoverflow.com/questions/5465170/text-run-is-not-in-unicode-normalization-form-c
"""

import unicodedata

from lib import *

def pass3(text):
    text = unicodedata.normalize('NFC', text)
    text = text.replace('စွွဲ၍', 'စွဲ၍')
    text = text.replace('Ä', '*')
    return text

if __name__ == '__main__':
    makedirs()
    for input_path in pass2_dir.glob('*.html'):
        output_path = pass3_dir / input_path.name
        print('Pass 3: {} -> {}'.format(input_path, output_path))
        with input_path.open('r', encoding='utf-8') as input:
            with output_path.open('w', encoding='utf-8') as output:
                output.write(pass3(input.read()))
