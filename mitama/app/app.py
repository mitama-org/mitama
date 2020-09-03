#!/usr/bin/python
from aiohttp import web

class App(web.Application):
    def __init__(self, meta):
        super().__init__(
            middlewares = [
                web.normalize_path_middleware(append_slash = True)
            ]
        )
        self.meta = meta
        self.name = meta.name
