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
from aiohttp_session import session_middleware
from aiohttp_session.cookie_storage import EncryptedCookieStorage
from jinja2 import Environment, FileSystemLoader
from mitama.conf import get_from_project_dir
from pathlib import Path
from mitama.http import Response, get_session
import os
import typing

from mitama.auth import AuthorizationError
from mitama.auth import password_hash, password_auth, get_jwt

config = get_from_project_dir()

view = Environment(
    enable_async=True,
    loader = FileSystemLoader([
        config._project_dir,
        Path(os.path.dirname(__file__)) / 'templates'
    ])
)

async def login(request):
    template = view.get_template('login.html')
    if request.method == 'POST':
        try:
            post = await request.post()
            result = password_auth(post['screen_name'], post['password'])
            sess = await get_session(request)
            sess['jwt_token'] = get_jwt(result)
            redirect_to = request.query.get('redirect_to', '/')
            return Response.redirect(
                redirect_to
            )
        except AuthorizationError as err:
            error = 'パスワード、またはログイン名が間違っています'
            return await Response.render(
                template,
                request,
                {
                    'error':error
                },
                status = 401
            )
    return await Response.render(
        template,
        request,
        status = 401
    )

async def logout(request):
    sess = await get_session()
    sess['jwt_token'] = None
    redirect_to = request.query.get('redirect_to', '/')
    return Response.redirect(redirect_to)

class Server():
    def __init__(self, port=8080):
        self.apps = dict()
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
        app.middlewares.insert(0, session_middleware(EncryptedCookieStorage(secret_key)))
        for k in self.apps:
            if k == '/':
                continue
            app.add_subapp(k, self.apps[k])
        web.run_app(app, port = self.port, access_log = None)
