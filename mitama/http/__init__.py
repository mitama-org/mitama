import base64, re
from http.server import ThreadingHTTPServer
from socketserver import StreamRequestHandler
from .request import Request
from .response import Response
from cryptography import fernet
from mitama.http.session import SessionMiddleware, EncryptedCookieStorage
from mitama.app import App

class _MainApp(App):
    def __init__(self, app_registry):
        self.app_registry = app_registry
        self._router = None
        super().__init__(name='_mitama', path='/', package = '_mitama')
    @property
    def router(self):
        if self._router == None or self.app_registry.changed:
            router = self.app_registry.router()
            router.add_middleware(SessionMiddleware)
            self._router = router
        return self._router

def run_app(app, port, request_factory = Request.parse_stream):
    class RequestHandler(StreamRequestHandler):
        def handle(self):
            request = request_factory(self.rfile)
            response = app(request)
            response.start(request, self.wfile)
    with ThreadingHTTPServer(('', int(port)), RequestHandler) as server:
        server.serve_forever()
