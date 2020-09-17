from jinja2 import *
from .app import App
from .router import Router
from .builder import Builder
from mitama.http import Request

class Controller():
    app = None
    async def handle(self, req: Request):
        pass

class Middleware():
    app = None
    async def process(self, req: Request, handler):
        pass

class StaticFileController():
    def __init__(self, path):
        self.path = path
    async def handle(self, req: Request):
        filename = self.path / req.path
        if filename.is_file():
            return Response()
        elif filename.is_dir():
            return Response()
        else:
            return Response(status = 404)
