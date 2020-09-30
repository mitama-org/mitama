#!/usr/bin/python
'''httpサーバー'''

import base64, re
from cryptography import fernet
from aiohttp import web
from mitama.http.session import SessionMiddleware, EncryptedCookieStorage
from mitama.conf import get_from_project_dir
from mitama.auth import AuthorizationError
from mitama.auth import password_hash, password_auth, get_jwt
from mitama.app import App, Middleware

class PathMiddleware(Middleware):
    async def process(self, request, handler):
        path_to_check = []
        if '?' in request.raw_path:
            path, query = request.raw_path.split('?', 1)
            query = '?' + query
        else:
            query = ''
            path = request.raw_path
        path_to_check.append(re.sub('//+', '/', path) + query)
        if not request.path.endswith('/'):
            path_to_check.append(path + '/' + query)
        path_to_check.append(re.sub('//+', '/', path + '/') + query)
        for path in path_to_check:
            resolves, request = await self._check_request_solves(request, path)
            if resolves:
                raise redirect_class(request.raw_path + query)
        return await handler(request)

class Server():
    def __init__(self, port=8080):
        self.port = port
        fernet_key = fernet.Fernet.generate_key()
        secret_key = base64.urlsafe_b64decode(fernet_key)
        self.session_middleware = SessionMiddleware(EncryptedCookieStorage(secret_key))
    def registry(self, registry):
        self.registry = registry
        self.registry._server = self
    def load_routes(self):
        self.router = self.registry.router()
        self.router.add_middlewares([
            self.session_middleware,
        ])
        if hasattr(self, '_app'):
            self._app.router = self.router
    def run(self):
        self.load_routes()
        class _App(App):
            router = self.router
        config = get_from_project_dir()
        self._app = _App(
            name = '_mitama',
            path = '/'
        )
        web.run_app(self._app.app, port = self.port, access_log = None)

