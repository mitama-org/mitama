from abc import ABCMeta, abstractmethod

from jinja2 import *

from .app import App
from .builder import Builder
from .hook import HookRegistry
from .http import Request
from .registry import AppRegistry
from .router import Router


class Controller:
    """MVCのControllerの基底クラス

    メソッドを記述すると、それをリクエスト処理に利用できる。
    ルーティング時にメソッドを特に指定しない場合はhandleメソッドが実行される。
    :param app: Controllerを起動するAppのインスタンスの参照
    :param view: Controllerが利用するJinja2のEnvironmentインスタンス
    """

    app = None
    view = None

    def __init__(self, app):
        self.app = app
        self.view = app.view

    def handle(self, request: Request):
        """リクエストハンドラ

        ルーティング時に特にメソッド名を指定しない場合にはこのメソッドが起動する。
        独自にメソッドを定義する場合にも、このメソッドと同じインターフェースを実装しなければならない。
        :param request: mitama.http.Requestのインスタンス
        :return: mitama.http.Responseのインスタンス
        """
        pass

    def __call__(self, request, method=None):
        if method == None:
            return self.handle(request)
        else:
            func = getattr(self, method)
            return func(request)


class Middleware(metaclass=ABCMeta):
    """Requestを加工するMiddlewareの抽象クラス

    processメソッドによって受け取ったRequestを変更し、handler（次のMiddleware、またはControllerのメソッド）に受け渡す。
    :param app: Middlewareを起動するAppのインスタンスの参照
    :param view: Middlewareが利用するJinja2のEnvironmentインスタンス
    """

    def __init__(self, app):
        self.app = app
        self.view = app.view

    @abstractmethod
    def process(self, request: Request, handler):
        """Middlewareのメイン処理

        Middlewareは必ずこのメソッドを実装しなければならない。
        :param request: mitama.http.Requestのインスタンス
        :param handler: requestを引数に受け取る関数（Middleware.process、またはControllerのリクエストハンドラ）
        """
        pass

    def __call__(self, request, handler):
        return self.process(request, handler)
