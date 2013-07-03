#!/usr/bin/env python

import os, sys

# See http://stackoverflow.com/questions/10095037/why-use-sys-path-appendpath-instead-of-sys-path-insert1-path
sys.path.insert(1, os.path.join(os.path.realpath(os.path.dirname(__file__)), 'python'))

import cherrypy
import config, root

cherrypy.engine.autoreload.files.add(config.global_conf_path)
cherrypy.engine.autoreload.files.add(config.local_conf_path)

if __name__ == '__main__':
    cherrypy.quickstart(root.Root(), config=config.config)
else:
    # For some reason, this mode requires global settings to be explicitly
    # injected.
    cherrypy.config.update(config.config['global'])
    cherrypy.tree.mount(root.Root(), config=config.config)
