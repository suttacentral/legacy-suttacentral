#!/usr/bin/env python

import httplib2
import random
import regex
import socket
import time
import threading
from urllib.parse import urlparse

import env
import scimm

MAX_THREADS = 40
MAX_URL_CHECKS = 5

def external_urls():
    imm = scimm.imm()
    for sutta in imm.suttas.values():
        for translation in sutta.translations:
            if not translation.url.startswith('/'):
                yield (translation.url, translation)

def check_url(url, obj):
    turl = regex.sub(r' ', '%20', url)
    host = urlparse(turl).netloc
    checks = 0
    h = httplib2.Http(timeout=30)
    while checks < MAX_URL_CHECKS:
        try:
            response, _ = h.request(turl, 'HEAD')
            if response.status != 503:
                status = response.status
                break
        except socket.timeout:
            status = 'Timed out'
            response = 'Timed out'
        checks += 1
        time.sleep(5 * checks * random.random())
    if status != 200:
        print('%s' % url)
        print('  Status: {}'.format(status))
        print('  Response: {}'.format(repr(response)))
        print('  Translation: {}'.format(repr(obj)))

def check_external_urls():
    for url, translation in external_urls():
        thread = threading.Thread(target=check_url, args=(url, translation))
        thread.start()
        while threading.active_count() > MAX_THREADS:
            time.sleep(0.1)

if __name__ == '__main__':
    check_external_urls()
