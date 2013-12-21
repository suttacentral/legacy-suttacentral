import bs4
import os
import pathlib
import regex
import sys
import textwrap
from bs4 import Tag
from functools import reduce

sys.path.insert(1, str(pathlib.Path('.').resolve().parents[1]))

base_dir = pathlib.Path('.')
originals_dir = base_dir / 'originals'
tmp_dir = base_dir / 'tmp'
pass1_dir = tmp_dir / 'pass1'
pass2_dir = tmp_dir / 'pass2'
pass3_dir = tmp_dir / 'pass3'
output_dir = base_dir / 'output'
output_dn_dir = output_dir / 'dn'
output_mn_dir = output_dir / 'mn'
output_sn_dir = output_dir / 'sn'

output_template = """\
<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<meta author="ပိဋကတ်တော် မြန်မာပြန်ဌာနမှ သုတ္တန် ပိဋကတ်တော်ကို ပါဠိဘာသာမှ ပြန်ဆိုသည်။">
<title>{title}</title>
{css_html}</head>
<body>
<div id="text" lang="my">
<div id="toc">
<div id="metaarea">
<p>ပိဋကတ်တော် မြန်မာပြန်ဌာနမှ သုတ္တန် ပိဋကတ်တော်ကို ပါဠိဘာသာမှ ပြန်ဆိုသည်။</p>
<p>သာသနာရေး ဦးစီးဌာနမှ ညွန်ကြားရေးမှူး ဦးဝင်းနိုင်က ပုံနှိပ်ထုတ်ဝေသည်။</p>
</div>
</div>
<section class="sutta">
<article>
<hgroup>
<h2>{division}</h2>
{vagga_html}<h1>{title}</h1>
</hgroup>
{content}</article>
</section>
</div>
</body>
</html>
"""

def output_html(title=None, division=None, content=None, vagga=None, css=False):
    assert title
    assert division
    assert content
    if vagga:
        vagga_html = '<h3>{}</h3>\n'.format(vagga)
    else:
        vagga_html = ''
    if css:
        css_html = '<link href="sc.css" rel="stylesheet" type="text/css">\n'
    else:
        css_html = ''
    return output_template.format(title=title, division=division,
        content=content, vagga_html=vagga_html, css_html=css_html)

def clean(text):
    return regex.sub(r'\s+', ' ', text.strip())

def makedirs():
    for dir in [pass1_dir, pass2_dir, pass3_dir, output_dn_dir,
                output_mn_dir, output_sn_dir]:
        if not dir.exists():
            dir.mkdir(parents=True)

def soup(text):
    return bs4.BeautifulSoup(text)

def soup_body_lines(text):
    def line_elements(el):
        return type(el) is Tag and hasattr(el, 'text') and \
               el.text.strip() != ''
    return filter(line_elements, soup(text).body)

def tagit(tag, text):
    return '<{0}>{1}</{0}>\n'.format(tag, text)

def dash_to_em(text):
    return text.replace('-','—')

def curly_quote(text):
    return ' '.join(map(curly_quote_word, text.split(' ')))

def curly_quote_word(word):
    # If the quotes are at (or near) the start of the word, then it's an opening
    # quote. Otherwise, it's a closing quote.
    #
    # ''မေတ္တာဟူသော -> “မေတ္တာဟူသော
    # နာကျင်မှုကင်းသည်ဖြစ်လတ္တံ့''ဟု -> နာကျင်မှုကင်းသည်ဖြစ်လတ္တံ့”ဟု
    # 
    # Pairs of quotes within a word get assigned as open and close quotes:
    #
    # 'ကရုဏာ' > ‘ကရုဏာ’
    while True:
        i = word.find("'")
        if i < 0:
            break
        if word[i+1:i+2] == "'":
            length = 2
        else:
            length = 1
        if i <= 1:
            if length == 1:
                quote = '‘'
            else:
                quote = '“'
        else:
            if length == 1:
                quote = '’'
            else:
                quote = '”'
        word = word[0:i] + quote + word[i+length:]
    return word

_log_file = (tmp_dir / 'log.txt').open('w', encoding='utf-8')

def log(msg):
    _log_file.write(msg + '\n')

def is_namo_tassa_line(text):
    return text.startswith('နမော တဿ ဘဂဝတော အရဟတော')

def is_translation_line(text):
    return text == 'မြန်မာပြန်'

def is_vagga_line(text):
    return text.endswith('ဝဂ်')

def is_sutta_line(text):
    return text.endswith('သုတ်') and _digit_re.match(text[0])

_numbers = list('ဝ၁၂၃၄၅၆၇၈၉')
_number_dict = { str(i): c for i, c in enumerate(_numbers) }
_digit_re = regex.compile('|'.join(_numbers))
_number_re = regex.compile("""^
                              ((?:{})+)       # the number
                              (\s*(?:-|။)\s*) # a breaker
                              (.*)            # everything else
                              $""".format(_digit_re.pattern),
                           regex.VERBOSE)

def burmize_number(n):
    return ''.join([_number_dict.get(c, '') for c in list(str(n))])

def parse_numbers(text):
    numbers = []
    while True:
        match = _number_re.match(text)
        if match:
            digits = [_numbers.index(c) for c in list(match[1])]
            number = reduce(lambda t, n: (t * 10) + n, digits, 0)
            numbers.append(number)
            text = match[3]
        else:
            break
    return numbers
