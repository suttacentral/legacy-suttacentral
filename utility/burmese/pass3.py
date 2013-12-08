#!/usr/bin/env python

"""Finalize output.

- Normalize Unicode issues.
- Add font-face.

See http://stackoverflow.com/questions/5465170/text-run-is-not-in-unicode-normalization-form-c
"""

import glob
import os.path
import unicodedata

FONTS_HTML = """\
<style>
@font-face {
    font-family: "Tharon Regular";
    src: url("tharlon-regular.ttf") format("truetype");
    font-weight: normal;
    font-style: normal;
}
body {
    font-family: "Tharon Regular";
}
</style>
"""

def convert(text):
    text = unicodedata.normalize('NFC', text)
    text = text.replace('</head>', '{}</head>'.format(FONTS_HTML))
    return text

for input_path in glob.glob('pass2/*.html'):
    output_path = 'pass3/{}'.format(os.path.basename(input_path))
    print('Converting {} to {}'.format(input_path, output_path))
    input = open(input_path, 'r', encoding='utf8')
    output = open(output_path, 'w', encoding='utf8')
    output.write(convert(input.read()))
