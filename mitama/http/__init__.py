#!/usr/bin/python
'''HTTP関連

サーバーの実装です。
'''
from aiohttp import web
from abc import ABCMeta, abstractmethod
import re

class Response(web.Response):
    '''レスポンスのクラス

    aiohttpのweb.Responseを拡張したものです。
    '''
    @classmethod
    async def render(cls, template, request, values = {}, **kwargs):
        '''HTMLを描画するレスポンスを返却します

        Jinja2のテンプレートにデータを入れてHTMLを生成し、Responseインスタンスを作成して返却します。
        テンプレート内部からはRequest内の非同期関数を呼び出すことができます。
        :param template: Jinja2テンプレート
        :param request: Requestインスタンス
        :param values: プレースホルダに入力するデータの辞書
        :param **kwargs: aiohttp.web.Responseに受け渡す、statusやheadersなどのデータ
        '''
        if 'content_type' not in kwargs:
            kwargs['content_type'] = 'text/html'
        values['request'] = request
        body = await template.render_async(values)
        return cls(text = body, **kwargs)
    @classmethod
    def redirect(cls, uri, status=302):
        '''リダイレクトします

        :param uri: リダイレクト先のURL
        :param status: リダイレクト時のステータスコード
        '''
        return cls(headers = {
            'Location': uri
        }, status = status)

class StreamResponse(web.StreamResponse):
    '''動画とかをレスポンスで返したいときはこれを使う（んだと思う）'''
    pass

class Request(web.Request):
    '''リクエストのクラス

    aiohttpのweb.Requestを拡張したものです。
    '''
    __dict_style = re.compile('([a-zA-Z0-9_\-.]+)\[([a-zA-Z0-9_\-.]*)\]')
    async def session(self):
        '''セッション情報を取得します

        :return: セッションの辞書データ
        '''
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
        '''リクエストボディのデータを取得します

        :return: リクエストボディのデータ
        '''
        post = await super().post()
        data = dict()
        for k,v in post.items():
            if not isinstance(v, web.FileField) and len(v) == 0:
                continue
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
