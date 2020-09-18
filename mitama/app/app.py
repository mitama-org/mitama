#!/usr/bin/python
from aiohttp import web
from yarl import URL
from jinja2 import Environment, FileSystemLoader
from pathlib import Path

class App:
    template_dir = 'templates';
    def __init__(self, **kwargs):
        kwargs['middlewares'] = [
            web.normalize_path_middleware(append_slash = True)
        ]
        self.app = web.Application()
        self.name = kwargs['name']
        self.path = kwargs['path']
        self.project_dir = Path(kwargs['project_dir'])
        self.install_dir = Path(kwargs['install_dir'])
        self.view= Environment(loader = FileSystemLoader(self.install_dir / self.template_dir))
        self.view.globals.update(convert_uri = self.convert_uri)
        for instance in self.instances:
            instance.app = self
            instance.view = self.view
            if hasattr(instance,  '__connected__'):
                instance.__connected__()
        if callable(self.router):
            router = self.router()
        else:
            router = self.router
        self.app.router.add_route('*', '/{tail:(?!login|logout).*}', router.match)
    def __getattr__(self, name):
        return getattr(self.app, name)
    def set_middleware(self, middlewares):
        self.app.middlewares.extend(middlewares)
    def convert_uri(self, uri):
        path = self.path
        if path[0] != '/':
            path = '/' + path
        if path[-1] == '/':
            path = path[0:-2]
        if uri[0] != '/':
            uri = '/' + uri
        return path + uri
    def revert_uri(self, uri):
        path = self.path
        if path[0] != '/':
            path = '/' + path
        if path[-1] == '/':
            path = path[0:-2]
        uri = str(uri.path)
        url = URL(uri[len(path):])
        return url
