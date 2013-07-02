import logging

mysql_settings = {
    'host': '127.0.0.1',
    'port' :3306,
    'user': 'root',
    'password': 'quality',
    'db': 'suttacen_m2'
    }
    
alt_mysql_settings = {
    'host': '127.0.0.1',
    'port' :3306,
    'user': 'root',
    'passwd': 'quality',
    'db': 'suttacen_m2'
    }

sqlite3_settings = {
    'db': './db/scdb.sqlite'
}

text_root = '/var/www/text/'

static_root = './static'

# A place for the dbr to put it's stuff.
dbr_cache = './dbr.cache'

# Perform resource-intensive run-time tests only if STRESS_TEST is True
RUNTIME_TESTS = True

# Raise exceptions and such which would be bad news on the live site.
DEBUG = True

# Configure Logging

logging.basicConfig(level=logging.DEBUG,
    format='{asctime}: {name}: {levelname}: {message}',
    datefmt='%m-%d %H:%M',
    style='{',
    filename='./sc.log')
console = logging.StreamHandler()
console.setLevel(logging.WARNING)
console.setFormatter(logging.Formatter('{name}: {levelname}: {message}', style='{'))
logging.root.addHandler(console)
del console
