#!/usr/bin/python
'''HTTP関連

    * サーバーの実装です。
'''
from aiohttp import web
from abc import ABCMeta, abstractmethod
import re

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
    __dict_style = re.compile('([a-zA-Z0-9_\-.]+)\[([a-zA-Z0-9_\-.]*)\]')
    async def session(self):
        sess = self.get('mitama_session')
        if sess is None:
            storage = self.get('mitama_session_storage')
            sess = await storage.load_session(self)
            self['mitama_session'] = sess
        return sess
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
    async def post(self):
        post = await super().post()
        data = dict()
        for k,v in post.items():
            match = self.__dict_style.match(k)
            if match!=None:
                name, key = match.group(1,2)
                if key == '':
                    if name not in data:
                        data[name] = list()
                    data[name].append(v)
                else:
                    if name not in data:
                        data[name] = dict()
                    data[name][key] = v
            else:
                data[k] = v
        return data
