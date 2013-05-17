import os
import cherrypy
import mysql.connector
from jinja2 import Environment, FileSystemLoader

BASE_PATH = os.path.realpath(os.path.dirname(__file__))

config = {
    '/': {
        'tools.staticdir.root': os.path.join(BASE_PATH, 'static'),
    },
    '/css': {
        'tools.staticdir.on': True,
        'tools.staticdir.dir': 'css'
    },
    '/js': {
        'tools.staticdir.on': True,
        'tools.staticdir.dir': 'js'
    }
}

dbconfig = {
    'user': 'suttacentral',
    'password': 'suttacentral',
    'database': 'suttacentral'
}

env = Environment(loader=FileSystemLoader('templates'))
db = mysql.connector.connect(**dbconfig)

class App:
    @cherrypy.expose
    def index(self):
        tmpl = env.get_template('index.html')
        cursor = db.cursor()
        cursor.execute("SELECT sutta_acronym, sutta_name from sutta LIMIT 10;")
        suttas = cursor.fetchall()
        return tmpl.render(suttas=suttas)

if __name__ == '__main__':
    cherrypy.quickstart(App(), config=config)
