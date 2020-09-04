#!/usr/bin/python
from aiohttp import web

class App:
    def __init__(self, meta):
        self.app = web.Application(
            middlewares = [
                web.normalize_path_middleware(append_slash = True)
            ]
        )
        self.meta = meta
        self.name = meta.name
    def __getattr__(self, name):
        return getattr(self.app, name)
