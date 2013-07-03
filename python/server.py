#!/usr/bin/env python

import os, sys
import cherrypy
import config, logger, root

logger.setup()

cherrypy.engine.autoreload.files.add(config.global_conf_path)
cherrypy.engine.autoreload.files.add(config.local_conf_path)

if __name__ == '__main__':
    cherrypy.quickstart(root.Root(), config=config)
else:
    # For some reason, this mode requires global settings to be explicitly
    # injected.
    cherrypy.config.update(config['global'])
    cherrypy.tree.mount(root.Root(), config=config)
