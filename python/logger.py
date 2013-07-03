"""A simple logging interface for SuttaCentral.

Usage:

    from logger import getLogger
    logger = getLogger(__name__)
    ...
    logger.info('my message')

"""

import logging
import config

def getLogger(name=None):
    return logging.getLogger(name)

def cherrypy_filter(record):
    return not record.name.startswith('cherrypy.error') and \
           not record.name.startswith('cherrypy.access')

formatter = logging.Formatter(
    fmt='{asctime}: {name}: {levelname}: {message}',
    datefmt='%m-%d %H:%M',
    style='{'
)

app_log = logging.FileHandler(config.app_log_file)
app_log.setLevel(getattr(logging, config.app_log_level))
app_log.addFilter(cherrypy_filter)
app_log.setFormatter(formatter)

console_log = logging.StreamHandler()
console_log.setLevel(getattr(logging, config.console_log_level))
console_log.addFilter(cherrypy_filter)
console_log.setFormatter(formatter)

def __setup():
    logging.root.setLevel(logging.NOTSET)
    logging.root.addHandler(app_log)
    logging.root.addHandler(console_log)

__setup()
