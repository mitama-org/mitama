#!/usr/bin/python

class App:
    def __init__(self, meta):
        self.routing = []
        self.meta = meta
        self.name = meta.name
    def add_routes(self, routes: list):
        for path, ctrl in routes:
            self.add_route(path, ctrl)
    def add_route(self, path, ctrl):
        self.routing.append((path, ctrl))
