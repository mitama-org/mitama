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
    apps = dict()
    def __init__(self, port=8080):
        self.port = port
    def add_app(self, app, _path):
        self.apps[_path] = app
    def run(self):
        if '/' in self.apps:
            app = self.apps['/']
        else:
            app = web.Application(middlewares = [
                web.normalize_path_middleware(append_slash = True)
            ])
        fernet_key = fernet.Fernet.generate_key()
        secret_key = base64.urlsafe_b64decode(fernet_key)
        setup(app, EncryptedCookieStorage(secret_key))
        for k in self.apps:
            if k == '/':
                continue
            app.add_subapp(k, self.apps[k])
        web.run_app(app, port=self.port, access_log = None)
