#!/usr/bin/env python

import cherrypy

from sc import config, logger
# Make sure to do this before importing root because it cascades into importing
# scimm which autostarts the imm updater thread.
logger.setup()

from sc import root, util

util.set_timezone()
cherrypy_controller = root.Root()
cherrypy_config = config.for_cherrypy()

if __name__ == '__main__':
    cherrypy.quickstart(cherrypy_controller, config=cherrypy_config)
else:
    # For some reason, this mode requires global settings to be explicitly
    # injected.
    cherrypy.config.update(cherrypy_config['global'])
    cherrypy.tree.mount(cherrypy_controller, config=cherrypy_config)
