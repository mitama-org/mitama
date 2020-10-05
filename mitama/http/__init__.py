import base64, re
import ssl
#from http.server import ThreadingHTTPServer
from http.server import HTTPServer
from socketserver import StreamRequestHandler
from .request import Request
from .response import Response
import threading


def run_app(app, port, request_factory = Request.parse_stream, ssl = False):
    class RequestHandler(StreamRequestHandler):
        def handle(self):
            request = request_factory(self.rfile)
            response = app(request)
            response.start(request, self.wfile)
    class SSLRequestHandler(StreamRequestHandler):
        def handle(self):
            request = request_factory(self.rfile, True)
            response = app(request)
            response.start(request, self.wfile)
    def serve():
        #with ThreadingHTTPServer(('', int(port)), RequestHandler) as server:
        with HTTPServer(('', int(port)), RequestHandler) as server:
            server.serve_forever()
    th_nossl = threading.Thread(name = 'nossl', target = serve)
    if ssl != False:
        def ssl_serve():
            #with ThreadingHTTPServer(('', int(ssl['port'])), SSLRequestHandler) as server:
            with HTTPServer(('', int(ssl['port'])), SSLRequestHandler) as server:
                if ssl!=False:
                    ctx = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
                    crtx.load_cert_chain(ssl['cert'], ssl['key'])
                    ctx.options |= ssl.OP_NO_TLSv1 | ssl.OP_NO_TLSv1_1
                    server.socket = ctx.wrap_socket(server.socket)
                server.serve_forever()
        th_ssl = threading.Thread(name = 'ssl', target = ssl_serve)
        th_ssl.start()
        th_nossl.start()
    else:
        th_nossl.start()
