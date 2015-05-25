"""SuttaCentral server environment.

Usage: cherryd -i sc.server

Note: This module is not intended to be imported from another module or
program.
"""
import logging
logger = logging.getLogger(__name__)


def _green_text(text):
    try:
        from colorama import Fore
        return Fore.GREEN + text + Fore.RESET
    except ImportError:
        return text
try:
    
    from sc import app, updater, config

    app.setup()
    app.mount()
except ImportError as e:
    logger.exception(e)
    cmd = 'pip install -r requirements.txt'
    logger.error('Missing dependency, try running: {}'.format(_green_text(cmd)))
    exit(1)
    
    
