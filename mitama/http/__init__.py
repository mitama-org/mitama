import base64, re
import ssl
from http.server import ThreadingHTTPServer
from socketserver import StreamRequestHandler
from .request import Request
from .response import Response


def run_app(app, port, request_factory = Request.parse_stream, ssl = False):
    class RequestHandler(StreamRequestHandler):
        def handle(self):
            request = request_factory(self.rfile)
            response = app(request)
            response.start(request, self.wfile)
    with ThreadingHTTPServer(('', int(port)), RequestHandler) as server:
        if ssl!=False:
            ctx = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
            crtx.load_cert_chain(ssl['cert'], ssl['key'])
            ctx.options |= ssl.OP_NO_TLSv1 | ssl.OP_NO_TLSv1_1
            server.socket = ctx.wrap_socket(server.socket)
        server.serve_forever()
