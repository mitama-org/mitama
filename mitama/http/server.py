#!/usr/bin/python
'''httpサーバー

    * てめえら喜べ、非同期だ。
    * ルーティングは完全にaiohttpのやつに頼る
    * アプリケーションごとにルーティングを定義したフォルダを作ってもらうはずなので、それを少し調整して一つの配列にマージして使う
    * ここではわりとしっかり目のMVC2のControllerを定義してやって、そのインターフェースをアプリに強制させる方式をとりたい
'''

from cryptography import fernet
import base64
from aiohttp import web
from aiohttp_session import setup
from aiohttp_session.cookie_storage import EncryptedCookieStorage
from . import Controller

class Server:
    routing = []
    def __init__(self, port=8080):
        self.port = port
    def add_routes(self, routes: list, _path):
        for path, ctrl in routes:
            self.add_route(_path+path if _path != '/' else path, ctrl)
    def add_route(self, path, ctrl):
        if type(ctrl) is str:
            handler = eval(ctrl)
        elif isinstance(ctrl, Controller):
            handler = ctrl.handle
        elif callable(ctrl):
            handler = ctrl
        else:
            raise TypeError(
                'Given controller is not correct type.'
                'Controller must be function, class which extends mitama.http.server.Controller,'
                'or a string whose name of the callable thing.'
            )
        self.routing.append(web.get(path, handler))
    def run(self):
        app = web.Application(middlewares = [
            web.normalize_path_middleware(append_slash = True)
        ])
        fernet_key = fernet.Fernet.generate_key()
        secret_key = base64.urlsafe_b64decode(fernet_key)
        setup(app, EncryptedCookieStorage(secret_key))
        app.add_routes(self.routing)
        web.run_app(app, port=self.port, access_log = None)
