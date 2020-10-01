from http.server import ThreadingHTTPServer
from socketserver import StreamRequestHandler
from .request import Request
import threading

def run_app(app, port, request_factory = Request.parse_stream):
    class RequestHandler(StreamRequestHandler):
        def handle(self):
            request = request_factory(self.rfile)
            response = app(request)
            response.start(self.wfile)
    with ThreadingHTTPServer(('', int(port)), RequestHandler) as server:
        server.serve_forever()
