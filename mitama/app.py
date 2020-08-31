from mitama.extra import _Singleton

class BaseMetadata(_Singleton):
    pass

class App:
    routing = []
    def __init__(self, meta):
        self.meta = meta
        self.name = meta.name
    def add_routes(self, routes: list):
        for path, ctrl in routes:
            self.add_route(path, ctrl)
    def add_route(self, path, ctrl):
        self.routing.append((path, ctrl))

