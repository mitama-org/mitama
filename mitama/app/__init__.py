from jinja2 import *
from .app import App
from .router import Router
from .builder import Builder
from mitama.http import Request, Response
from pathlib import Path
from mimetypes import guess_type
import os

class Controller():
    app = None
    async def handle(self, req: Request):
        pass

class Middleware():
    app = None
    async def process(self, req: Request, handler):
        pass

class StaticFileController(Controller):
    def __init__(self, *paths):
        super().__init__()
        self.paths = list(paths)
    def __connected__(self):
        if len(self.paths) == 0:
            self.paths.append(self.app.install_dir / 'static')
        else:
            for path in paths:
                self.paths.append(Path(path))
    async def handle(self, req: Request):
        for path in self.paths:
            filename = path / req.params['path']
            if filename.is_file():
                mime = guess_type(filename)
                with open(filename) as f:
                    return Response(body = f.read(), headers={
                        'content-type': mime[0]
                    })
        for path in self.paths:
            filename = path / '404.html'
            if filename.is_file():
                with open(filename) as f:
                    return await Response(text = f.read(), status = 404, headers = {
                        'content-type': 'text/html'
                    })
        template = self._view.get_template('404.html')
        return await Response.render(template, req, status = 404)
