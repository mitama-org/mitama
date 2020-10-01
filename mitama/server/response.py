from http.server import BaseHTTPRequestHandler
import http.cookies
from abc import ABCMeta, abstractmethod

class ResponseBase(metaclass = ABCMeta):
    _version = 'HTTP/1.1'
    def __init__(self, status = 200, reason = None, headers = {}):
        self.headers = headers
        self._status = int(status)
        if reason is None:
            try:
                self._reason = BaseHTTPRequestHandler.responses[self._status][0]
            except:
                self._reason = ''
        else:
            self._reason = reason
        self._cookies = http.cookies.SimpleCookie()
    def set_cookie(self, key, value = None, **kwargs):
        self._cookies[key] = value
        for k,v in kwargs.items():
            self._cookies[key][k] = v
    @abstractmethod
    def start(self, stream):
        pass

class Response(ResponseBase):
    def __init__(self, body = None, text = '', headers = {}, status = 200, reason = None, content_type = None, charset = None):
        super().__init__(headers = headers, status = status, reason = reason)
        if body is not None and text is not None:
            raise ValueError('body and text are not allowed together')
        if text is not None:
            if not isinstance(text, str):
                raise TypeError('')
            if content_type is None:
                content_type = 'text/html'
            if charset is None:
                charset = 'utf-8'
            body = text.encode(charset)
            text = None
        else:
            if content_type is not None:
                if charset is not None:
                    content_type += '; charset='+charset
        self.content_type = content_type
        self.body = body
    def start(self, stream):
        stream.write(('%s %s %s\r\n' % (self._version, self._status, self._reason)).encode())
        for k,v in self.headers.items():
            stream.write(('%s: %s\r\n' % (k, v)).encode())
        stream.write(self._cookies.output().encode())
        stream.write(('Content-Type: %s\r\n' % self.content_type).encode())
        stream.write('\r\n'.encode())
        stream.write(self.body)

class StreamResponse(ResponseBase):
    def __init__(self, body = None, headers = {}, status = 200, reason = None, content_type = None, charset = None):
        super().__init__(headers = headers, status = status, reason = reason)
        self.content_type = content_type
        if charset is not None:
            self.content_type += '; charset='+charset
        if body is not None:
            self.body = body
        else:
            self.body = list()
    def start(self, stream):
        stream.write(('%s %s %s\r\n' % (self._version, self._status, self._reason)).encode())
        for k,v in self.headers.items():
            stream.write(('%s: %s\r\n' % (k, v)).encode())
        stream.write(self._cookies.output().encode())
        stream.write(('Content-Type: %s\r\n' % self.content_type).encode())
        stream.write('\r\n'.encode())
        for chunk in self.body:
            stream.write(chunk)

