import logging
import config

def getLogger(name=None):
    return logging.getLogger(name)

def __setup():
    logging.basicConfig(level=logging.DEBUG,
        format='{asctime}: {name}: {levelname}: {message}',
        datefmt='%m-%d %H:%M',
        style='{',
        filename=config.app_log_file)
    console = logging.StreamHandler()
    console.setLevel(logging.WARNING)
    console.setFormatter(logging.Formatter('{name}: {levelname}: {message}', style='{'))
    logging.root.addHandler(console)

__setup()
