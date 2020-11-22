import os
from mitama.app import Controller
from mitama.app.http import Request, Response
from jinja2 import *
from mimetypes import add_type, guess_type
from pathlib import Path

add_type('application/json', '.map')

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

