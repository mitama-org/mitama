#!/usr/bin/python
'''httpサーバー

    * てめえら喜べ、非同期だ。
    * ルーティングは完全にaiohttpのやつに頼る
    * アプリケーションごとにルーティングを定義したフォルダを作ってもらうはずなので、それを少し調整して一つの配列にマージして使う
    * ここではわりとしっかり目のMVC2のControllerを定義してやって、そのインターフェースをアプリに強制させる方式をとりたい
'''

import base64
from cryptography import fernet
from aiohttp import web
from mitama.http.session import SessionMiddleware, EncryptedCookieStorage
from mitama.conf import get_from_project_dir
from mitama.auth import AuthorizationError
from mitama.auth import password_hash, password_auth, get_jwt
from mitama.app import App, Middleware

class PathMiddleware(Middleware):
    async def _check_request_solves(self, request, path):
        alt_request = request.clone(rel_url = path)
        match_info = await request.app.router.resolve(alt_request)
        alt_request._match_info = match_info
        if match_info.http_exception is None:
            return True, alt_request
        return False, request
    async def process(self, request, handler):
        if isinstance(request.match_info.route, SystemRoute):
            paths_to_check = []
            if '?' in request.raw_path:
                path, query = request.raw_path.split('?', 1)
                query = '?' + query
            else:
                query = ''
                path = request.raw_path
            path_to_check.append(re.sub('//+', '/', path))
            if not request.path.endswith('/'):
                path_to_check.append(path + '/')
            path_to_check.append(re.sub('//+', '/', path + '/'))
            for path in paths_to_check:
                resolves, request = await self._check_request_solves(request, path)
                if resolves:
                    raise redirect_class(request.raw_path + query)
        return await handler(request)

class Server():
    def __init__(self, port=8080):
        self.port = port
    def registry(self, registry):
        self.registry = registry
        self.registry._server = self
    def run(self):
        router = self.registry.router()
        fernet_key = fernet.Fernet.generate_key()
        secret_key = base64.urlsafe_b64decode(fernet_key)
        path_middleware = PathMiddleware()
        session_middleware = SessionMiddleware(EncryptedCookieStorage(secret_key))
        router.add_middlewares([
            session_middleware,
            path_middleware
        ])
        class _App(App):
            @property
            def router(self):
                return router
        config = get_from_project_dir()
        app = _App(
            name = '_mitama',
            path = '/'
        )
        web.run_app(app.app, port = self.port, access_log = None)
