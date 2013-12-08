#!/usr/bin/env python

"""Create simplified HTML from original HTML found on pitakataw.com."""

import bs4
import glob
import os.path

TEMPLATE = """\
<!DOCTYPE html>
<html lang="my">
<head>
<meta charset="utf-8">
<title>{}</title>
</head>
<body>
{}
</body>
</html>
"""

def convert(input_text):
    soup = bs4.BeautifulSoup(input_text)
    title = soup.select('title')[0].text
    doc = soup.select('.blogPost')[0]
    result = []
    for el in doc.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p', 'center']):
        if 'blogger-labels' in el.get('class', []):
            continue
        if el.name == 'center':
            result.append('<hr />')
        else:
            text = el.text.replace('\n', ' ')
            result.append('<{}>{}</{}>'.format(el.name, text, el.name))
    return TEMPLATE.format(title, '\n'.join(result))

for input_path in glob.glob('originals/*.html'):
    output_path = 'pass1/{}'.format(os.path.basename(input_path).lower())
    print('Converting {} to {}'.format(input_path, output_path))
    input = open(input_path, 'r', encoding='utf8')
    output = open(output_path, 'w', encoding='utf8')
    output.write(convert(input.read()))
