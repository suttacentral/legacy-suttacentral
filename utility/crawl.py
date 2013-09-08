#!/usr/bin/env python
"""Sutta Central website crawl utility

This utility was created specifically for crawling Sutta Central and
creating a reasonably clean and functional set of HTML files and other
assets for offline use.

I checked out the usual suspects like HTTrack and wget and was not
satisfied (partly the problem with those utilities are they are
"respectful", so it takes them a long time to crawl such a big site.
This utility takes mere minutes CPU cores permitting. They also create
(even more) complicated folder structures and uglier urls.
Finally and most critically they can't do the little custom tweaks to
enable or disable disfunctional features).

Please note it is probably better NOT to run this on the server since it
runs unthrottled. Really it's designed to be run on a developers box.

"""

import lxml.html, regex, os, urllib, collections
from urllib.request import urlopen
from urllib.parse import urljoin

server = 'http://localhost:8800'
baseurl = '/'
start = server + baseurl
out = 'out'

taskqueue = collections.deque()
seen = set()

taskqueue.append(baseurl)
taskqueue.extend(['/js/pi2en_dict_0.03.js', '/js/zh2en_dict_0.04s.js'])

def fixurl(old_url):
    url = old_url
    fixurl.url = url

    if url == '/':
        url = 'index'
    elif url.endswith('/'):
        url = url[:-1]
    elif '/#' in url:
        url = url.replace('/#', '#')
    if url[0] == '/':
        url = url[1:]
    return url

def getending(url):
    if '.' in url:
        ending = url.split('.')[-1]
        if regex.match(r'\d', ending):
            ending = ''
    else:
        ending = ''
    return ending

def fixcss(text, url, _cache={}):
    try:
        return _cache[url]
    except KeyError:
        pass
    def callback(m):
        url = m[0]
        if url not in seen:
            taskqueue.append(regex.match('[^#?]+', url)[0])
        return url[0].replace('/', '../') + url[1:]
    result = regex.sub(r"(?<=url\(')[^']+(?='\))", callback, text)
    result = result.replace('a.tran:not([href^="/"])', 'a.tran[href^="http"]')
    result = result.replace('.search {', '#navsearch {display:none}\n.search {')
    _cache[url] = result
    return result

def process(url):
    fullurl = urljoin(server, url)
    print(fullurl)
    ending = getending(url)
    new_url = fixurl(url)
    if not ending:
        ending = 'html'
        new_url += '.html'
    depth = len(new_url.split('/')) - 1
    filename = os.path.join(out, new_url)
    try:
        os.makedirs(os.path.dirname(filename))
    except OSError:
        pass
    with urlopen(fullurl) as f:
        bytes = f.read()

    if ending not in ('html', 'js', 'css'):
        with open(filename, 'wb') as f:
            f.write(bytes)
        return

    text = bytes.decode(encoding='utf8')

    if ending in ('css', 'js'):
        if ending == 'css':
            text = fixcss(text, url)
        with open(filename, 'w') as f:
            f.write(text)
        return
    dom = lxml.html.fromstring(text)
    process.dom = dom
    for script in dom.cssselect('script[src*=jquery]'):
        script.drop_tree()
    for script in dom.iter('script'):
        if script.text and script.text.startswith('window.jQuery'):
            script.text = None
            script.attrib['src'] = '/js/vendor/jquery-1.9.1.min.js'
    if '/pi' in url:
        dom.body.append(dom.makeelement('script', {'src':'/js/pi2en_dict_0.03.js'}))
    if '/zh' in url:
        dom.body.append(dom.makeelement('script', {'src':'/js/zh2en_dict_0.04s.js'}))
    
    for a in dom.cssselect('[href], [src]'):
        attr = 'href'
        if 'src' in a.attrib:
            attr = 'src'
        try:
            href = a.attrib[attr]
        except KeyError:
            continue
        if not href:
            continue
        if href.startswith('#'):
            continue
        if href.startswith(baseurl):
            if href not in seen:
                taskqueue.append(href)
                seen.add(href)
        new_href = fixurl(href)
        if depth > 0:
            new_href = '../' * depth + new_href
        ending = getending(href)
        if not ending:
            new_href += '.html'

        a.attrib[attr] = new_href

    with open(filename, 'wb') as f:
        f.write(lxml.html.tostring(dom, encoding='utf8'))
        
errors = open('errors.txt', 'w')

import time
start = time.time()
count = 0
while len(taskqueue) > 0:
    try:
        url = taskqueue.popleft()
        process(url)
        count += 1
    except (urllib.error.HTTPError, urllib.error.URLError) as e:
        errors.write("{}: {}".format(str(e), url))
        continue
total = time.time() - start
print('{} pages downloaded in {} seconds, {} pages per second.'.format(count, total, count / total))