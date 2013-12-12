import bs4
import os
import pathlib
import regex
import textwrap

base_dir = pathlib.Path('.')
originals_dir = base_dir / 'originals'
tmp_dir = base_dir / 'tmp'
pass1_dir = tmp_dir / 'pass1'
pass2_dir = tmp_dir / 'pass2'
pass3_dir = tmp_dir / 'pass3'
output_dir = base_dir / 'output'
output_dn_dir = output_dir / 'dn'
output_mn_dir = output_dir / 'mn'

numbers_re = regex.compile(r'๐|၁|၂|၃|၄|၅|၆|၇|၈|၉')

output_template = """\
<!DOCTYPE html>
<html lang="my">
<head>
    <meta charset="UTF-8"><title>{title}</title>
    <link rel="stylesheet" href="sc.css" type="text/css">
</head><body>
<div id="text" lang="my"><section class="sutta"><article>
<hgroup>
    <h2>{division}</h2>
    <h1>{title}</h1>
</hgroup>
{content}
</article></section></div>
</body></html>
"""

def clean(text):
    return regex.sub(r'\s+', ' ', text.strip())

def makedirs():
    for dir in [pass1_dir, pass2_dir, pass3_dir, output_dn_dir, output_mn_dir]:
        if not dir.exists():
            os.makedirs(str(dir))

def soup(text):
    return bs4.BeautifulSoup(text)

def tagit(tag, text):
    text = clean(text)
    text = textwrap.fill(text, width=78)
    if '\n' in text:
        text = '\n' + textwrap.indent(text, '  ') + '\n'
    return '<{0}>{1}</{0}>\n'.format(tag, text)
