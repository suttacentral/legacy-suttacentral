#!/usr/bin/env python

import cherrypy

import config
import logger
# Make sure to do this before importing root because it cascades into importing
# scimm which autostarts the imm updater thread.
logger.setup()

import root
import util

util.set_timezone()

if __name__ == '__main__':
    cherrypy.quickstart(root.Root(), config=config)
else:
    # For some reason, this mode requires global settings to be explicitly
    # injected.
    cherrypy.config.update(config['global'])
    cherrypy.tree.mount(root.Root(), config=config)
