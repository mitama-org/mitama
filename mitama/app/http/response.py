import http.cookies
import json
import types
from abc import ABCMeta, abstractmethod
from http.server import BaseHTTPRequestHandler


class ResponseBase(metaclass=ABCMeta):
    _version = "HTTP/1.1"

    def __init__(self, status=200, reason=None, headers={}):
        self.headers = headers
        self._status = int(status)
        if reason is None:
            try:
                self._reason = BaseHTTPRequestHandler.responses[self._status][0]
            except KeyError:
                self._reason = ""
        else:
            self._reason = reason
        self._cookies = http.cookies.SimpleCookie()

    def set_cookie(self, key, value=None, **kwargs):
        self._cookies[key] = value or ""
        for k, v in kwargs.items():
            self._cookies[key][k] = v or ""

    @abstractmethod
    def start(self, request, stream):
        pass


class Response(ResponseBase):
    def __init__(
        self,
        body=None,
        text=None,
        headers={},
        status=200,
        reason=None,
        content_type=None,
        charset=None,
    ):
        super().__init__(headers=headers, status=status, reason=reason)
        if body is not None and text is not None:
            raise ValueError("body and text are not allowed together")
        if text is not None:
            if not isinstance(text, str):
                raise TypeError("")
            if content_type is None:
                content_type = "text/html"
            if charset is None:
                charset = "utf-8"
            body = text.encode(charset)
            text = None
        else:
            if content_type is not None:
                if charset is not None:
                    content_type += "; charset=" + charset
            else:
                content_type = "text/html"
        self.content_type = content_type
        self.body = body

    def start(self, request, start_response):
        headers = list()
        for kv in self.headers.items():
            headers.append(kv)
        cookies = self._cookies.output(header="")
        if len(cookies) > 0:
            headers.extend([("Set-Cookie", cookie) for cookie in cookies.split("\r\n")])
        headers.append(("Content-Type", self.content_type))
        start_response(("%s %s" % (self._status, self._reason)), headers)
        if callable(self.body):
            return [self.body(request)]
        elif isinstance(self.body, types.GeneratorType):
            return [*self.body]
        elif self.body is not None:
            return [self.body]
        else:
            return []

    @classmethod
    def json(cls, d, **kwargs):
        if "content_type" not in kwargs:
            kwargs["content_type"] = "application/json"
        return cls(body=json.dumps(d).encode(), **kwargs)

    @classmethod
    def render(cls, template, values={}, **kwargs):
        """HTMLを描画するレスポンスを返却します

        Jinja2のテンプレートにデータを入れてHTMLを生成し、Responseインスタンスを作成して返却します。
        テンプレート内部からはRequest内の非同期関数を呼び出すことができます。
        :param template: Jinja2テンプレート
        :param request: Requestインスタンス
        :param values: プレースホルダに入力するデータの辞書
        :param **kwargs: aiohttp.web.Responseに受け渡す、statusやheadersなどのデータ
        """

        def render(request):
            values["request"] = request
            return template.render(values).encode()

        return cls(body=render, **kwargs)

    @classmethod
    def redirect(cls, uri, status=302):
        """リダイレクトします

        :param uri: リダイレクト先のURL
        :param status: リダイレクト時のステータスコード
        """
        return cls(headers={"Location": uri}, status=status)


class StreamResponse(ResponseBase):
    def __init__(
        self,
        body=None,
        headers={},
        status=200,
        reason=None,
        content_type=None,
        charset=None,
    ):
        super().__init__(headers=headers, status=status, reason=reason)
        self.content_type = content_type
        if charset is not None:
            self.content_type += "; charset=" + charset
        if body is not None:
            self.body = body
        else:
            self.body = list()

    def start_wsgi(self, request, start_response):
        headers = list()
        for kv in self.headers.items():
            headers.append(kv)
        cookies = self._cookies.output(attrs=[], header="")
        if len(cookies) > 0:
            headers.extend([("Set-Cookie", cookie) for cookie in cookies.strip("\r\n")])
        headers.append(("Content-Type", self.content_type))

        def content():
            nonlocal self, start_response, request, headers
            start_response(("%s %s" % (self._status, self._reason)), headers)
            for chunk in self.body:
                if callable(chunk):
                    yield chunk(request)
                elif chunk is not None:
                    yield chunk
        return content()

    def start(self, request, stream):
        stream.write(
            ("%s %s %s\r\n" % (self._version, self._status, self._reason)).encode()
        )
        for k, v in self.headers.items():
            stream.write(("%s: %s\r\n" % (k, v)).encode())
        stream.write(self._cookies.output().encode())
        stream.write(("Content-Type: %s\r\n" % self.content_type).encode())
        stream.write("\r\n".encode())
        for chunk in self.body:
            if callable(chunk):
                stream.write(chunk())
            else:
                stream.write(chunk)
