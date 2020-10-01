import cgi
import http
import http.cookies

class _Cookies():
    def __init__(cookies):
        self._cookies = cookies
    def __getitem__(self, key):
        if key in self._cookies:
            return self._cookies[key].value
        else:
            raise KeyError('')

class _RequestPayload():
    def __init__(self, field_storage):
        self._field_storage = field_storage
    def __getitem__(self, key):
        if key not in self._field_storage:
            raise KeyError
        elif self._field_storage[key].file is None:
            return self._field_storage[key].value
        else:
            return self._field_storage[key]
    @classmethod
    def parse_body(cls, rfile, content_type, length):
        environ = {
            'REQUEST_METHOD': 'POST'
        }
        headers = {
            'content-type': content_type,
            'content-length': length
        }
        fs = cgi.FieldStorage(rfile, environ = environ, headers = headers)
        payload = cls(fs)
        return payload

class Request():
    MessageClass = http.client.HTTPMessage
    def __init__(self, method, path, version, headers, rfile):
        self._method = method
        self._raw_path = path
        path = path.split('?')
        if len(path) == 2:
            path, query = path
            self._path = path
            self._query = query
        else:
            self._path = path
            self._query = None
        self._version = version
        self._headers = headers
        self._rfile = rfile
    @property
    def method(self):
        return self._method
    @property
    def raw_path(self):
        return self._raw_path
    @property
    def path(self):
        return self._path
    @property
    def query(self):
        return self._query
    @property
    def version(self):
        return self._version
    @property
    def headers(self):
        return self._headers
    @property
    def cookies(self):
        if hasattr(self, '_cookies'):
            return self._cookies
        else:
            C = http.cookies.BaseCookie()
            cookie_headers = self._headers.get_all('cookie', [])
            cookie_str = '; '.join(cookie_headers)
            C.load(cookie_str)
            self._cookies = _Cookie(C)
            return self._cookies
    def post(self):
        content_type = self._headers.get('Content-Type')
        length = int(self._headers.get('Content-Length'))
        if content_type in ('multipart/form-data', 'application/x-www-form-urlencoded'):
            parsed_body = _RequestPayload.parse_body(self._rfile, content_type, length)
        elif content_type == 'application/json':
            payload = self._rfile.read()
            parsed_body = json.loads(payload)
        else:
            parsed_body = None
        return parsed_body
    @classmethod
    def parse_stream(cls, rfile):
        words = rfile.readline().decode().rstrip('\r\n').split(' ')
        version = words[-1]
        if not 2 <= len(words) <= 3:
            raise Exception('Bad Request')
        command, path = words[:2]
        if len(words) == 2:
            close_connection = True
            if command!='GET':
                raise Exception('Bad Request')
        try:
            headers = http.client.parse_headers(rfile, _class = cls.MessageClass)
        except http.client.LineTooLong as err:
            raise Exception('')
        except http.client.HTTPException as err:
            raise Exception('')
        return cls(command, path, version, headers, rfile)
