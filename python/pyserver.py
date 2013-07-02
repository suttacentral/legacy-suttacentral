#!/usr/bin/env python3.3

from wsgiref.simple_server import make_server

from wsgi import application

httpd = make_server('', 8001, application)
print("Serving HTTP on port 8001...")

httpd.serve_forever()