import cherrypy
import os
import time

import sc
from sc import config, logger, root

_approot = None

def get_root():
    global _approot
    if not _approot:
        _approot = root.Root()
    return _approot

def mount():
    """Mount the application on cherrypy."""

    cherrypy_config = config.for_cherrypy()
    # For some reason, the global settings need to be explicitly injected.
    cherrypy.config.update(cherrypy_config['global'])
    
    cherrypy.tree.mount(get_root(), config=cherrypy_config)


def setup(test=False):
    """Setup the application environment."""

    # Set default timezone.
    os.environ['TZ'] = sc.config.timezone
    time.tzset()

    # Add the configuration files to trigger autoreload.
    cherrypy.engine.autoreload.files.add(str(sc.global_config_path))
    cherrypy.engine.autoreload.files.add(str(sc.local_config_path))

    # Do not use autoreloader against plumbum
    cherrypy.engine.autoreload.match = r'^(?!plumbum).+'

    logger.setup()
