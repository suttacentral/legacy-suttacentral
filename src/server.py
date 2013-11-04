#!/usr/bin/env python

import cherrypy
import config, logger, root

logger.setup()

if __name__ == '__main__':
    cherrypy.quickstart(root.Root(), config=config)
else:
    # For some reason, this mode requires global settings to be explicitly
    # injected.
    cherrypy.config.update(config['global'])
    cherrypy.tree.mount(root.Root(), config=config)
