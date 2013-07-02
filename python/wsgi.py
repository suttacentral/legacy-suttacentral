#!/usr/bin/env python3.3
import sys, cherrypy
sys.stdout = sys.stderr
from root import Root

cherrypy.config.update({
'environment': 'embedded',
'log.error_file':'/home/nandiya/Programming/python/wsgi/log/errors.txt',
'log.access_file':'/home/nandiya/Programming/python/wsgi/log/access.txt',
})

application = cherrypy.Application(Root(), script_name=None, config=None)
    