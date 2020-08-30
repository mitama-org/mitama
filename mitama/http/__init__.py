#!/usr/bin/python
'''HTTP関連

    * サーバーの実装です。
'''
from aiohttp import web
from aiohttp_session import get_session
from abc import ABCMeta, abstractmethod

class Response(web.Response):
    pass

class StreamResponse(web.StreamResponse):
    pass

class Request(web.Request):
    pass

class Controller(metaclass = ABCMeta):
    @abstractmethod
    async def handle(self, req: Request):
        pass

