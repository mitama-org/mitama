import base64
import re
import ssl

from gevent.pywsgi import WSGIServer
from geventwebsocket.handler import WebSocketHandler

from .request import Request
from .response import Response


def run_app(app, port):
    server = WSGIServer(
        ("localhost", int(port)),
        app.wsgi,
        handler_class=WebSocketHandler
    )
    server.serve_forever()
