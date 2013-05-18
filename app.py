import os
import cherrypy
import sqlalchemy
from jinja2 import Environment, FileSystemLoader

BASE_PATH = os.path.realpath(os.path.dirname(__file__))
CONFIG_PATH = os.path.join(BASE_PATH, 'app.conf')
LOCAL_CONFIG_PATH = os.path.join(BASE_PATH, 'local.conf')
STATIC_BASE_PATH = os.path.join(BASE_PATH, 'static')

#
# Configuration
#

def deep_update(a, b):
    for k, v in b.items():
        if k in a and isinstance(a[k], dict) and isinstance(b[k], dict):
            deep_update(a[k], b[k])
        else:
            a[k] = v
    return a

config = cherrypy.lib.reprconf.as_dict(CONFIG_PATH)
try:
    deep_update(config, cherrypy.lib.reprconf.as_dict(LOCAL_CONFIG_PATH))
except IOError:
    pass

# Absolutize any relative paths that cherrypy can't handle.
for key, subdict in config.items():
    if key[0] == '/':
        subkey = 'tools.staticfile.filename'
        if subkey in subdict:
            subdict[subkey] = os.path.join(STATIC_BASE_PATH, subdict[subkey])

config['/']['tools.staticdir.root'] = STATIC_BASE_PATH

cherrypy.engine.autoreload.files.add(os.path.join(BASE_PATH, 'app.conf'))
cherrypy.engine.autoreload.files.add(os.path.join(BASE_PATH, 'local.conf'))

#
# Database Setup
#

db_connection = ('mysql+mysqlconnector://' +
    '%(user)s:%(password)s@%(host)s:%(port)s/%(database)s') % config['db']
# Automatically recycle connections after one hour because the MySQL server
# automatically disconnects connections after about 8 hours of non-use.
db_engine = sqlalchemy.create_engine(db_connection, pool_recycle=3600)

def db_connection():
    """
        Return a db connection pessimistically.
        See http://docs.sqlalchemy.org/en/rel_0_8/core/pooling.html
    """
    global db_engine
    cursor = db_engine.connect()
    try:
        cursor.execute('SELECT 1')
    except sqlalchemy.exc.OperationalError as e:
        print('Lost connection to database, trying to reconnect')
        cursor.close()
        cursor = db_engine.connect()
    return cursor

# App

env = Environment(loader=FileSystemLoader('templates'))

def error_page_404(status, message, traceback, version):
    return open(os.path.join(STATIC_BASE_PATH, '404.html'), 'r').read()

class App:

    _cp_config = {
        'error_page.404': error_page_404
    }

    @cherrypy.expose
    def index(self):
        cursor = db_connection()
        suttas = cursor.execute(
            "SELECT sutta_acronym, sutta_name from sutta LIMIT 15;").fetchall()
        tmpl = env.get_template('index.html')
        return tmpl.render(suttas=suttas)

#
# Start
#

if __name__ == '__main__':
    cherrypy.quickstart(App(), config=config)
else:
    # For some reason, this mode requires global settings to be explicitly
    # injected.
    cherrypy.config.update(config['global'])
    cherrypy.tree.mount(App(), config=config)
