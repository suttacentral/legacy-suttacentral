import cherrypy
import os
import time

import sc
from sc import config, logger, root


def mount():
    """Mount the application on cherrypy."""

    cherrypy_config = config.for_cherrypy()
    # For some reason, the global settings need to be explicitly injected.
    cherrypy.config.update(cherrypy_config['global'])
    cherrypy.tree.mount(root.Root(), config=cherrypy_config)


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
