""" Subset the chinese dictionaries to only entries which exist on SC

Presently two chinese dictionaries are used, a Buddhist dictionary,
and a fallback dictionary (the unicode one).

This program uses the original files as-is, for two reasons, firstly,
the buddhdic.txt is update regulary. Secondly, it might be desired
to change the information pulled out of them.

Two subsettings are performed, firstly, only a subset of the information
in the dictionaries is kept, secondly, only a subset of the entries in
the dictionaries are kept - those being the ideographs which are actually
used on SuttaCentral.

"""

import env
import sc
import argparse
import regex
from sc.tools import html
from pathlib import Path
import tempfile
import logging
import webassets
import gzip
import time
from urllib.request import urlopen
from urllib.error import HTTPError
from zipfile import ZipFile

# Paths and urls, these are quite close to being static.
js_script_data_dir = sc.static_dir / 'js' / 'data'

lzh2en_data_script_names_file = js_script_data_dir / 'lzh2en-data-scripts-names.js'
fallback_stem = 'lzh2en-fallback'
maindata_stem = 'lzh2en-maindata'

buddhdic_file = sc.tmp_dir / 'buddhdic.txt.gz'
buddhdic_url = 'http://www.acmuller.net/download/buddhdic.txt.gz'

unihanzip_file = sc.tmp_dir / 'Unihan.zip'
unihanzip_url = 'http://www.unicode.org/Public/zipped/6.3.0/Unihan.zip'
unihan_readings_filename = 'Unihan_Readings.txt'

if buddhdic_file.exists() and unihanzip_file.exists():
    age = max(time.time() - buddhdic_file.stat().st_mtime, time.time() - unihanzip_file.stat().st_mtime)
    if age < 14 * 24 * 60 * 60:
        logging.info('Nothing to be done')
        exit(0)

def parse_args():
    parser = argparse.ArgumentParser(
        description='Build Chinese Lookup Dictionary Data Scripts',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('-m', '--minify', help="Minify and version Javascript Output", action='store_true')
    parser.add_argument('-v', '--verbose', help="Log more information", action='store_true')
    parser.add_argument('-q', '--quiet', help="Show only error", action='store_true')
    return parser.parse_args()


class BuddhdicBuilder:
    def __init__(self, existing, seen=None):
        self.existing = existing
        self.seen = set()
        if seen:
            self.seen.update(seen)
    warnings = None
    def process(self, srcfo):
        skipped = []
        found = []
        pinyin_match = regex.compile(r'Pinyin: (.*)').match
        # The source file is not a true XML tree so we need to jump
        # through some hoops. Yay, hoops!
        with tempfile.NamedTemporaryFile('w+') as truetree:
            truetree.write('<root>')
            truetree.writelines(srcfo)
            truetree.write('</root>')
            truetree.flush()
            truetree.seek(0)
            root = html.parse(truetree.name).getroot()
        self.root = root
        entries = []
        for entry in root.iter('entry'):
            head = pinyin = meaning = None
            
            try:
                head = entry.text.strip()
                for e in entry:
                    m = pinyin_match(e.text_content())
                    if m:
                        pinyin = m[1]
                        break
                        
                meaning = entry.select_one('b').tail.lstrip(': ')
                
                if not head or not pinyin or not meaning:
                    logging.warning('Incomplete buddhdic entry: {!s}'.format(entry))

                if self.existing.issuperset(head):
                    entries.append('"{}": {}'.format(head, [pinyin, meaning]))
                    self.seen.update(head)
                    found.append((head, meaning))
                else:
                    skipped.append((head, meaning))
            except:
                print(head, pinyin, meaning)
                print(str(entry))
        if skipped:
            logging.info('{} entries do and {} entries do not appear in SuttaCentral texts'.format(len(found), len(skipped)))
            if self.args.verbose:
                logging.info('Entries which do not appear: ')
                logging.info(', '.join('{}: {}'.format(head, meaning) for head, meaning in skipped))
        return 'sc.lzh2enData = {\n' + ',\n'.join(entries) + '\n}'

class FallbackBuilder:
    def __init__(self, existing, seen=None):
        self.existing = existing
        self.seen = set()
        if seen:
            self.seen.update(seen)

    first = True
    def writeout(self, igraph, out):
        
        char = chr(int(igraph['code'], 16))
        if char not in self.existing or char in self.seen:
            return

        definition = igraph.get('kDefinition', '')
        definition = regex.sub(r' U\+\w+', '', definition)

        phon = set()
        mn = igraph.get('kMandarin', None)
        hu = igraph.get('kHanyuPinlu', None)
        hn = igraph.get('kHanyuPinyin', None)
        if hn:
            hn = regex.sub(r'\d+\.\d+:', '', hn)
        if hu:
            hu = regex.sub(r'\(\d+\)', '', hu)
        for p in [mn, hu, hn]:
            if p:
                phon.update(regex.split(r'[, ]+', p))
        phon = ",".join(sorted(phon))

        if not phon:
            return
        
        if not self.first:
            out.write(',\n')
        else:
            self.first = False
        out.write('\'{}\': {}'.format(char, [phon, definition]))
    
    def process(self, srcfo):
        fields = set()
        current = None

        outfo = tempfile.TemporaryFile('w+')
        
        outfo.write('sc.lzh2enFallbackData = {')
        
        for lineno, line in enumerate(srcfo):
            if line.startswith('#') or line.isspace():
                continue
            m = regex.match(r'U\+(?<code>\w+)\s+(?<field>\w+)\s+(?<content>.*)', line)
            if not m:
                print('{}: {}'.format(lineno + 1,line))
            fields.add(m['field'])
            
            if not current:
                current = {'code': m['code']}
            elif current['code'] != m['code']:
                self.writeout(current, outfo)
                current = {'code': m['code']}

            current[m['field']] = m['content']

        outfo.write('\n}\n')
        outfo.flush()
        outfo.seek(0)
        return outfo.read()

def generate_version(string):
    import hashlib
    return hashlib.md5(string.encode()).hexdigest()[:10]

def minify_js(js_string):
    # Now I could use the webassets built in ... stuff ... to do this
    # but here's the truth - it makes me happy to hack stuff together.
    from webassets.filter.rjsmin.rjsmin import jsmin
    
    out_string = jsmin(js_string)
    version = generate_version(out_string)
    return  version + '.min', out_string

def writeout_js(stem, js_string, js_process_fn):
    """ Minifies and saves js, returns the versioned filename used """
    if js_process_fn:
        version, min_js = js_process_fn(js_string)
        outfile = js_script_data_dir / '{}-{}.js'.format(stem, version)
    else:
        version, min_js = '', js_string
        outfile = js_script_data_dir / '{}.js'.format(stem)
    if not outfile.parent.exists():
        outfile.parent.mkdir(parents=True)
    
    with outfile.open('w') as f:
        f.write(min_js)
    
    return outfile

def discover_existing_charcodes():
    seen = set()
    for file in sc.text_dir.glob('lzh/**/*.html'):
        with file.open(encoding='utf8') as f:
            for line in f:
                seen.update(line)
    return seen

def clean(stem, latest):
    # Wipe out the older versions of the file.
    for file in js_script_data_dir.glob(stem + '*'):
        if file != latest:
            file.unlink()    

args = parse_args()
loglevel = logging.INFO
if args.quiet:
    loglevel = logging.ERROR
if args.verbose:
    loglevel = logging.DEBUG
    
logging.basicConfig(format='%(levelname)s: %(message)s', level=loglevel)

existing_charcodes = discover_existing_charcodes()


bdbuilder = BuddhdicBuilder(existing=existing_charcodes)
bdbuilder.args = args

fbbuilder = FallbackBuilder(existing=existing_charcodes, seen=bdbuilder.seen)

js_process_fn = None
if args.minify:
    js_process_fn = minify_js

from urllib.request import urlopen

def dl_file(url, target_file):
    try:
        logging.info('Downloading {}'.format(target_file.name))
        with urlopen(url) as response:
            try:
                outf = target_file.open('wb')
                while True:
                    chunk = response.read(4096)
                    if not chunk:
                        break
                    outf.write(chunk)
                    
                outf.close()
                logging.info('{} downloaded okay'.format(target_file.name))
            except:
                target_file.unlink()
                raise
    except HTTPError as e:
        logging.error('{code}: Failed to download file {url}, previously built script data will still be used'.format(url=url, code=e.code))
        exit(0)    

dl_file(buddhdic_url, buddhdic_file)
    

with gzip.open(str(buddhdic_file), 'rt', encoding='utf8') as srcfo:
    bdstr = bdbuilder.process(srcfo)

maindata_file = writeout_js(maindata_stem, bdstr, js_process_fn)


dl_file(unihanzip_url, unihanzip_file)
with ZipFile(str(unihanzip_file)) as zipf:
    with tempfile.TemporaryDirectory() as tmpdir_name:
        filename = zipf.extract(unihan_readings_filename, tmpdir_name)
        with open(filename, 'r', encoding='utf8') as srcfo:
            fbstr = fbbuilder.process(srcfo)

fallback_file = writeout_js(fallback_stem, fbstr, js_process_fn)

with lzh2en_data_script_names_file.open('w', encoding='utf8') as f:
    f.write('// This file was created automatically and should not be modified manually.\n')
    f.write('sc.lzh2enDataScripts = {};'.format(
        ['data/' + maindata_file.name, 'data/' + fallback_file.name]))

clean(maindata_stem, maindata_file)
clean(fallback_stem, fallback_file)
logging.info('Build completed OK, files have been registered.')
