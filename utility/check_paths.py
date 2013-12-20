#!/usr/bin/env python

import cherrypy
import regex

import env

from sc import config, logger, root, scimm, show, util

def paths():
    dbr = scimm.imm()
    for page in show.STATIC_PAGES:
        yield ('/' + page, 'STATIC')
    for division in dbr.divisions.values():
        yield ('/' + division.uid, division)
        if division.has_subdivisions():
            yield ('/' + division.uid + '/full', division)
            for subdivision in division.subdivisions:
                yield ('/' + subdivision.uid, subdivision)
    for sutta in dbr.suttas.values():
        yield ('/' + sutta.uid, sutta)
        if sutta.text_ref:
            url = sutta.text_ref.url
            if url and url.startswith('/'):
                yield (url, sutta)
        for translation in sutta.translations:
            if translation.url and translation.url.startswith('/'):
                yield (translation.url, translation)

def get_path(path):
    path = regex.sub(r'#.*$', '', path) # chop fragment
    app = cherrypy.tree.apps['']
    local = cherrypy.lib.httputil.Host('127.0.0.1', 50000, '')
    remote = cherrypy.lib.httputil.Host('127.0.0.1', 50001, '')
    request, _ = app.get_serving(local, remote, 'http', 'HTTP/1.1')
    response = request.run('GET', path, '', 'HTTP/1.1', [('Host', '127.0.0.1')], None)
    if response.output_status.decode('utf-8') != '200 OK':
        raise Exception('Unexpected response: %s' % response.output_status)
    response.collapse_body()
    return len(response.body[0]) > 0

def check_paths():
    for path, obj in paths():
        try:
            result = get_path(path)
            exception = None
        except Exception as e:
            result = False
            exception = e
        if not result:
            print(path)
            print('  Exception: %s' % repr(exception))
            print('  Object: %s' % repr(obj))

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
    util.set_timezone()
    cherrypy.config.update(config['global'])
    cherrypy.server.unsubscribe()
    cherrypy.tree.mount(root.Root(), config=config.for_cherrypy())
    cherrypy.engine.start()

if __name__ == '__main__':
    setup()
    check_paths()
    cherrypy.engine.exit()
