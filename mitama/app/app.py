#!/usr/bin/python
from aiohttp import web
from yarl import URL

class App:
    def __init__(self, meta, **kwargs):
        kwargs['middlewares'] = [
            web.normalize_path_middleware(append_slash = True)
        ] + (kwargs['middlewares'] if 'middlewares' in kwargs else [])
        self.app = web.Application(
            **kwargs
        )
        self.meta = meta
        self.name = meta.name
    def __getattr__(self, name):
        return getattr(self.app, name)
    def convert_uri(self, uri):
        path = self.meta.path
        if path[0] != '/':
            path = '/' + path
        if path[-1] == '/':
            path = path[0:-2]
        if uri[0] != '/':
            uri = '/' + uri
        return path + uri
    def revert_uri(self, uri):
        path = self.meta.path
        if path[0] != '/':
            path = '/' + path
        if path[-1] == '/':
            path = path[0:-2]
        uri = str(uri.path)
        url = URL(uri[len(path):])
        print(url)
        return url
