from jinja2 import *
from .app import App, _MainApp
from .router import Router
from .builder import Builder
from .registry import AppRegistry
from mitama.http import Request, Response
from pathlib import Path
from mimetypes import add_type, guess_type
from abc import ABCMeta, abstractmethod
import os

add_type('application/json', '.map')

class Controller():
    '''MVCのControllerの基底クラス

    メソッドを記述すると、それをリクエスト処理に利用できる。
    ルーティング時にメソッドを特に指定しない場合はhandleメソッドが実行される。
    :param app: Controllerを起動するAppのインスタンスの参照
    :param view: Controllerが利用するJinja2のEnvironmentインスタンス
    '''
    app = None
    view = None
    def __init__(self, app):
        self.app = app
        self.view = app.view
    def handle(self, request: Request):
        '''リクエストハンドラ

        ルーティング時に特にメソッド名を指定しない場合にはこのメソッドが起動する。
        独自にメソッドを定義する場合にも、このメソッドと同じインターフェースを実装しなければならない。
        :param request: mitama.http.Requestのインスタンス
        :return: mitama.http.Responseのインスタンス
        '''
        pass
    def __call__(self, request, method = None):
        if method == None:
            return self.handle(request)
        else:
            func = getattr(self, method)
            return func(request)

class Middleware(metaclass = ABCMeta):
    '''Requestを加工するMiddlewareの抽象クラス

    processメソッドによって受け取ったRequestを変更し、handler（次のMiddleware、またはControllerのメソッド）に受け渡す。
    :param app: Middlewareを起動するAppのインスタンスの参照
    :param view: Middlewareが利用するJinja2のEnvironmentインスタンス
    '''
    def __init__(self, app):
        self.app = app
        self.view = app.view
    @abstractmethod
    def process(self, request: Request, handler):
        '''Middlewareのメイン処理

        Middlewareは必ずこのメソッドを実装しなければならない。
        :param request: mitama.http.Requestのインスタンス
        :param handler: requestを引数に受け取る関数（Middleware.process、またはControllerのリクエストハンドラ）
        '''
        pass
    def __call__(self, request, handler):
        return self.process(request, handler)

def static_files(*paths):
    paths_ = list(paths)
    class StaticFileController(Controller):
        '''静的ファイルを配信するController

        デフォルトではアプリのパッケージ内の :file:`static/` の中身を配信する。
        '''
        paths = paths_
        def __init__(self, app):
            super().__init__(app)
            app_mod_dir = Path(os.path.dirname(__file__))
            self.view = Environment(
                loader = FileSystemLoader([
                    app_mod_dir / 'templates',
                    app_mod_dir / '../http/templates'
                ])
            )
            if len(self.paths) == 0:
                self.paths.append(self.app.install_dir / 'static')
        def handle(self, req: Request):
            for path in self.paths:
                filename = path / req.params['path']
                if filename.is_file():
                    mime = guess_type(str(filename)) or ('application/octet-stream', )
                    with open(filename, 'rb') as f:
                        return Response(body = f.read(), content_type = mime[0])
            for path in self.paths:
                filename = path / '404.html'
                if filename.is_file():
                    with open(filename) as f:
                        return Response(text = f.read(), status = 404, headers = {
                            'content-type': 'text/html'
                        })
            template = self.view.get_template('404.html')
            return Response.render(template, status = 404)
    return StaticFileController

