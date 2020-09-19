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
        values['request'] = request
        body = await template.render_async(values)
        return cls(text = body, **kwargs)
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
    @classmethod
    def from_request(cls, request):
        return cls(
            message = request._message,
            payload = request._payload,
            protocol = request._protocol,
            payload_writer = request._payload_writer,
            task = request._task,
            loop = request._loop,
            state = request._state,
            client_max_size = request._client_max_size,
            host = request.host,
            remote = request.remote
        )
