#!/usr/bin/env python

"""SuttaCentral Offline Crawl Utility

This utility was created specifically for crawling SuttaCentral and
creating a reasonably clean and functional set of HTML files and other
assets for offline use.

Nandiya checked out the usual suspects like HTTrack and wget and was not
satisfied (partly the problem with those utilities are they are
"respectful", so it takes them a long time to crawl such a big site.
This utility takes mere minutes CPU cores permitting. They also create
(even more) complicated folder structures and uglier urls.

Features are enabled/disabled in the SuttaCentral code by checking for the
offline cookie flag.
"""

import argparse, collections, os, regex, sys, time, urllib, urllib.request
import env
import sc
import json
import pathlib
from lxml import html
from urllib.parse import urljoin

def parse_args():
    parser = argparse.ArgumentParser(
        description='SuttaCentral Offline Crawl Utility',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('host', type=str, help='the host to crawl')
    parser.add_argument('dir', type=str, help='output directory')
    parser.add_argument('-w', '--wait', type=float, default=0.0,
        help='time to wait between requests in seconds')
    parser.add_argument('--omit', type=str, default='',
        help='Do not crawl pages for these language codes, comma or space seperated')
    parser.add_argument('-q', '--quiet', action='store_true',
        help='suppress non-errors from output')
    return parser.parse_args()

opener = urllib.request.build_opener()
opener.addheaders = [e for e in opener.addheaders if e[0] != 'User-agent'] + [('User-agent', 'SC Offline Build Crawler')]
opener.addheaders.append(('Cookie', 'offline=1'))
def readurl(url):    
    with opener.open(url) as f:
        return f.read()

def addtotaskqueue(url):
    global taskqueue, seen
    url = fixurl(url)
    if url not in seen:
        taskqueue.append(url)
        seen.add(url)

def fixurl(url):
    """
        /a/b/   -> /a/b
        /a/b/#c -> /a/b
        /a/b/?c=1 -> /a/b
    """
    return regex.sub(r'(.)/?([#?].*)?$', r'\1', url)

def getending(url):
    if '.' in url:
        ending = url.split('.')[-1]
        if regex.match(r'\d', ending):
            ending = ''
    else:
        ending = ''
    return ending

def fixcss(text, depth):
    """A hack that only works on sc.css."""
    def callback(m):
        url = m[2]
        addtotaskqueue(url)
        return 'url({}{}{}{})'.format(m[1] or '', '../' * depth, url[1:], m[3] or '')
    return regex.sub(r'url\(([\'"])?(/[^\'")]+)([\'"])?\)', callback, text,
        flags=regex.MULTILINE)

def process(host, url, omit_codes=None, omit_rex=None, timeout=30):
    global output_dir
    fullurl = urljoin(host, url)
    ending = getending(url)
    new_url = fixurl(url)[1:]
    if new_url == '':
        new_url = 'index'
    if not ending:
        ending = 'html'
        new_url += '.html'
    depth = len(new_url.split('/')) - 1
    outfile = output_dir / new_url
    
    if not outfile.parent.exists():
        try:
            outfile.parent.mkdir(parents=True)
        except OSError:
            sys.stderr.write('Failed to create folder: {}\n'.format(outfile.parent))
            return
    pagedata = readurl(fullurl)

    if ending not in ('html', 'js', 'css'):
        with outfile.open('wb') as f:
            f.write(pagedata)
        return


    if ending in ('css', 'js'):
        text = pagedata.decode(encoding='utf8')
        if ending == 'css':
            text = fixcss(text, depth)
        with outfile.open('w', encoding='utf8') as f:
            f.write(text)
        return

    # We need to be very careful and explicit with lxml to handle utf8
    # correctly. See http://stackoverflow.com/questions/15302125/html-encoding-and-lxml-parsing
    parser = html.HTMLParser(encoding='utf8')
    root = html.fromstring(pagedata, parser=parser)
    
    if omit_codes:
        s = root.cssselect('script#sc_text_info')
        if s:
            text_info = s[0]
            jso = json.loads(text_info.text)
            jso["all_lang_codes"] = [code for code in jso["all_lang_codes"] if code not in omit_codes]
            text_info.text = json.dumps(jso)
    
    for a in root.cssselect('[href], [src]'):
        attr = 'href'
        if 'src' in a.attrib:
            attr = 'src'
        try:
            href = a.attrib[attr]
        except KeyError:
            continue
        # If omit_rex is defined, and matches href, then absolutize link
        # and do not crawl target page.
        if omit_rex and omit_rex.search(href) or omit_rex.search(a.text_content()):
            a.set(attr, 'https://legacy.suttacentral.net/' + a.get(attr))
            continue
        if not href or not href.startswith('/'):
            continue
        addtotaskqueue(href)
        new_href = fixurl(href)[1:]
        if new_href == '':
            new_href = 'index'
        if depth > 0:
            new_href = '../' * depth + new_href
        ending = getending(href)
        if not ending:
            new_href += '.html'

        a.attrib[attr] = new_href

    with outfile.open('wb') as f:
        f.write(b'<!DOCTYPE html>\n')
        f.write(html.tostring(root, encoding='utf8'))

if __name__ == '__main__':

    args = parse_args()
    host = 'http://{}'.format(args.host)
    output_dir = pathlib.Path(args.dir)
    quiet = args.quiet
    wait = args.wait
    extra_omit = {'sht-lookup'}
    if args.omit:
        omit_codes = {s for s in regex.split(r'[ ,]', args.omit) if s != ''}
    else:
        omit_codes = set()
    omit_rex = regex.compile(r'\b({})\b(?!-)'.format('|'.join(omit_codes | extra_omit)))

    taskqueue = collections.deque()
    seen = set()
    addtotaskqueue('/')
    # Add js files which are requested via AJAX thus lacking
    # href or src references.
    tomatch = ['zh', 'pi']
    for file in sc.static_dir.glob('js/**/*.js'):
        filename = file.name
        for string in tomatch:
            if string in filename:
                addtotaskqueue('/' + str(file.relative_to(sc.static_dir)))
                break

    start = time.time()
    count = 0
    while len(taskqueue) > 0:
        try:
            path = taskqueue.popleft()
            if not quiet:
                print(path)
            process(host, path, omit_codes, omit_rex)
            count += 1
        except (urllib.error.HTTPError, urllib.error.URLError) as e:
            sys.stderr.write("{}: {}\n".format(path, str(e)))
        if wait > 0:
            time.sleep(wait)

    total = time.time() - start
    if not quiet:
        print('{} pages downloaded in {} seconds, {} pages per second.'.format(count, total, round(count / total)))
    if count < 1:
        sys.exit(1)
