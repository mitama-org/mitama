from mitama.extra import _Singleton
from mitama.db import Database, get_app_engine
from sqlalchemy import orm

class BaseMetadata(_Singleton):
    pass

class App:
    routing = []
    def __init__(self, meta):
        self.name = meta.name
    def add_routes(self, routes: list):
        for path, ctrl in routes:
            self.add_route(path, ctrl)
    def add_route(self, path, ctrl):
        self.routing.append((path, ctrl))
    def run(self):
        app = web.Application(middlewares = [
            web.normalize_path_middleware(append_slash = True)
        ])
        app.add_routes(self.routing)
    def database(self, model = None, metadata = None, query_class = orm.Query):
        db = Database(model, metadata, query_class)
        db.set_engine(get_app_engine(self.name))
        return db


