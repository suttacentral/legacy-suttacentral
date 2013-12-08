#!/usr/bin/env python

import env
import cherrypy, httplib2, random, re, time, threading
from urllib.parse import urlparse
import config, logger, root, scdb

MAX_THREADS = 100
MAX_URL_CHECKS = 5

def external_urls():
    dbr = scdb.getDBR()
    for sutta in dbr.suttas.values():
        for translation in sutta.translations:
            if not translation.url.startswith('/'):
                yield (translation.url, translation)

def check_url(url, obj):
    turl = re.sub(r' ', '%20', url)
    host = urlparse(turl).netloc
    checks = 0
    h = httplib2.Http(timeout=30)
    while checks < MAX_URL_CHECKS:
        try:
            response, _ = h.request(turl, 'HEAD')
        except socket.timeout:
            status = 'Timed out'
            response = 'Timed out'
            break
        if response.status != 503:
            status = response.status
            break
        checks += 1
        time.sleep(5 * checks * random.random())
    if status != 200:
        print('%s' % url)
        print('  Status: %d' % status)
        print('  Response: %s' % repr(response))
        print('  Translation: %s' % repr(obj))

def check_external_urls():
    for url, translation in external_urls():
        thread = threading.Thread(target=check_url, args=(url, translation))
        thread.start()
        while threading.active_count() > MAX_THREADS:
            time.sleep(0.1)

def setup():
    config['global'].update({
        'environment': 'test_suite',
        'log.access_file': '',
        'log.error_file': '',
        'log.screen': False,
    })
    config['app'].update({
        'app_log_level': 'CRITICAL',
        'console_log_level': 'CRITICAL',
    })
    logger.setup()
    cherrypy.config.update(config['global'])
    cherrypy.server.unsubscribe()
    cherrypy.tree.mount(root.Root(), config=config)

if __name__ == '__main__':
    setup()
    check_external_urls()
