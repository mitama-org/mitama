import base64, re
import ssl
from http.server import HTTPServer
from socketserver import StreamRequestHandler
from .request import Request
from .response import Response
from wsgiref import simple_server

def run_app(app, port, request_factory = Request.parse_stream):
    with simple_server.make_server('', int(port), app.wsgi) as server:
        server.serve_forever()
