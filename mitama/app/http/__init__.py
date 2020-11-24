import base64
import re
import ssl
from http.server import HTTPServer
from socketserver import StreamRequestHandler
from wsgiref import simple_server

from .request import Request
from .response import Response


def run_app(app, port, request_factory=Request.parse_stream):
    with simple_server.make_server("", int(port), app.wsgi) as server:
        server.serve_forever()
