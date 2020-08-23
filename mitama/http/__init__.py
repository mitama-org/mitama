#!/usr/bin/python
'''HTTP関連

    * サーバーの実装です。
'''
from aiohttp import web
from sqlalchemy import orm
from abc import ABCMeta, abstractmethod
from mitama.extra import _Singleton
from mitama.db import Database, get_app_engine

class Response(web.Response):
    pass
class StreamResponse(web.StreamResponse):
    pass
class Request(web.Request):
    pass
class Controller(metaclass = ABCMeta):
    @abstractmethod
    async def handle(self, req: Request):
        pass

class App:
    routing = []
    def __init__(self, meta):
        self.name = meta.name
    def add_routes(self, routes: list):
        for path, ctrl in routes:
            self.add_route(path, ctrl)
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
        self.routing.append((path, handler))
    def run(self):
        app = web.Application(middlewares = [
            web.normalize_path_middleware(append_slash = True)
        ])
        app.add_routes(self.routing)
    def database(self, model = None, metadata = None, query_class = orm.Query):
        db = Database(model, metadata, query_class)
        db.set_engine(get_app_engine(self.name))
        return db

def create_app_metadata():
    class Metadata(_Singleton):
        pass
    return Metadata
