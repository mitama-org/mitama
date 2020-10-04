import base64, re
from http.server import ThreadingHTTPServer
from socketserver import StreamRequestHandler
from .request import Request
from .response import Response


def run_app(app, port, request_factory = Request.parse_stream):
    class RequestHandler(StreamRequestHandler):
        def handle(self):
            request = request_factory(self.rfile)
            response = app(request)
            response.start(request, self.wfile)
    with ThreadingHTTPServer(('', int(port)), RequestHandler) as server:
        server.serve_forever()
