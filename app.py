import os
import cherrypy
import mysql.connector
from jinja2 import Environment, FileSystemLoader

BASE_PATH = os.path.realpath(os.path.dirname(__file__))
CONFIG_PATH = os.path.join(BASE_PATH, 'app.conf')
LOCALCONFIG_PATH = os.path.join(BASE_PATH, 'local.conf')

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
    deep_update(config, cherrypy.lib.reprconf.as_dict(LOCALCONFIG_PATH))
except IOError:
    pass
deep_update(config, {'/': {
    'tools.staticdir.root': os.path.join(BASE_PATH, 'static')
}})

cherrypy.engine.autoreload.files.add(os.path.join(BASE_PATH, 'app.conf'))
cherrypy.engine.autoreload.files.add(os.path.join(BASE_PATH, 'local.conf'))

#
# App
#

env = Environment(loader=FileSystemLoader('templates'))
db = mysql.connector.connect(**config['db'])

class App:
    @cherrypy.expose
    def index(self):
        cursor = db.cursor()
        cursor.execute("SELECT sutta_acronym, sutta_name from sutta LIMIT 15;")
        suttas = cursor.fetchall()
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
