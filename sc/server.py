"""SuttaCentral server environment.

Can be used with cherryd:
cherryd -i sc.server

Or to run interactively:
>>> import sc.server
>>> sc.server.run_interactive()

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
    from sc import app, config

    app.setup()
    app.mount()
except ImportError as e:
    logger.exception(e)
    cmd = 'pip install -r requirements.txt'
    logger.error('Missing dependency, try running: {}'.format(_green_text(cmd)))
    exit(1)

def run_interactive():
    """The same as cherrypy.quickstart, but don't block."""
    from cherrypy import engine
    
    # This is what quickstart does but we don't block
    engine.signals.subscribe()
    engine.start()
    #engine.block()
    
