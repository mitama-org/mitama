#!/usr/bin/python
'''HTTP関連

    * サーバーの実装です。
'''
from aiohttp import web
from aiohttp_session import get_session
from abc import ABCMeta, abstractmethod

class Response(web.Response):
    @classmethod
    async def render(cls, template, request, values = {}, **kwargs):
        if 'content_type' not in kwargs:
            kwargs['content_type'] = 'text/html'
        values = dict(values, **(await request.post()))
        return cls(text = template.render(values), **kwargs)
    @classmethod
    def redirect(cls, uri, status=302):
        return cls(headers = {
            'Location': uri
        }, status = status)

class StreamResponse(web.StreamResponse):
    pass

class Request(web.Request):
    async def session(self):
        return await get_session(self)

