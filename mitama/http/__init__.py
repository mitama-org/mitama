#!/usr/bin/python
'''HTTP関連

    * サーバーの実装です。
'''
from aiohttp import web
from aiohttp_session import get_session
from abc import ABCMeta, abstractmethod
from aiohttp.web import middleware

class Response(web.Response):
    @classmethod
    def render(cls, template, values = {}, **kwargs):
        if 'content_type' not in kwargs:
            kwargs['content_type'] = 'text/html'
        return cls(text = template.render(values), **kwargs)
    pass

class StreamResponse(web.StreamResponse):
    pass

class Request(web.Request):
    pass

class Controller(metaclass = ABCMeta):
    @abstractmethod
    async def handle(self, req: Request):
        pass

