import time
import json
import base64
from cryptography import fernet
from collections.abc import MutableMapping
from mitama.http import Response

class Session(MutableMapping):
    def __init__(self, identity, *, data, new, max_age = None):
        self._changed = False
        self._mapping = {}
        self._identity = identity if data != {} else None
        self._new = new if data != {} else True
        self._max_age = max_age
        created = data.get('created', None) if data else None
        session_data = data.get('session', None) if data else None
        now = int(time.time())
        age = now - created if created else now
        if max_age is not None and age > max_age:
            session_data = None
        if self._new or created is None:
            self._created = now
        else:
            self._created = created

        if session_data is not None:
            self._mapping.update(session_data)
    @property
    def new(self):
        return self._new
    @property
    def identity(self):
        return self._identity
    @property
    def created(self):
        return self._created
    @property
    def empty(self):
        return not bool(self._mapping)
    @property
    def max_age(self):
        return self._max_age
    @max_age.setter
    def max_age(self, value):
        self._max_age = value
    def changed(self):
        self._changed = True
    def invalidate(self):
        self._changed = True
        self._mapping = {}
    def set_new_identity(self, identity):
        if not self._new:
            raise RuntimeError("Can't change identity for a session which is not new")
        self._identity = identity
    def __len__(self):
        return len(self._mapping)
    def __iter__(self):
        return iter(self._mapping)
    def __containers__(self, key):
        return key in self._mapping
    def __getitem__(self, key):
        return self._mapping[key]
    def __setitem__(self, key, value):
        self._mapping[key] = value
        self._changed = True
    def __delitem__(self, key):
        del self._mapping[key]
        self._changed = True

class EncryptedCookieStorage():
    def __init__(self, secret_key, *, cookie_name = 'MITAMA_SESSION',
                 domain = None, max_age = None, path = '/',
                 secure = None, httponly = True, encoder = json.dumps,
                 decoder = json.loads):
        self._cookie_name = cookie_name
        self._cookie_params = dict(domain = domain,
                                   max_age = max_age,
                                   path = path,
                                   secure = secure,
                                   httponly = httponly)
        self._max_age = max_age
        self._encoder = encoder
        self._decoder = decoder
        if isinstance(secret_key, str):
            pass
        elif isinstance(secret_key, (bytes, bytearray)):
            secret_key = base64.urlsafe_b64encode(secret_key)
        self._fernet = fernet.Fernet(secret_key)
    @property
    def cookie_name(self):
        return self._cookie_name
    @property
    def max_age(self):
        return self._max_age
    @property
    def cookie_params(self):
        return self._cookie_params
    def _get_session_data(self, session):
        if not session.empty:
            data = {
                'created': session.created,
                'session': session._mapping
            }
        else:
            data = {}
        return data
    def load_session(self, request):
        cookie = self.load_cookie(request)
        if cookie is None:
            return Session(None, data = None, new = True, max_age = self.max_age)
        else:
            try:
                data = self._decoder(
                    self._fernet.decrypt(
                        cookie.encode('utf-8'),
                        ttl = self._max_age
                    ).decode('utf-8')
                )
                return Session(None, data = data, new = False, max_age = self.max_age)
            except:
                return Session(None, data = None, new = True, max_age = self.max_age)
    def save_session(self, request, response, session):
        if session.empty:
            return self.save_cookie(response, '', max_age = session.max_age)
        cookie_data = self._encoder(
            self._get_session_data(session)
        ).encode('utf-8')
        self.save_cookie(
            response,
            self._fernet.encrypt(cookie_data).decode('utf-8'),
            max_age = session.max_age)
    def load_cookie(self, request):
        cookie = request.cookies.get(self._cookie_name)
        return cookie
    def save_cookie(self, response, cookie_data, *, max_age = None):
        params = dict(self._cookie_params)
        params_ = dict()
        for k in params.keys():
            params_[k.replace('_', '-')] = params[k]
        if max_age is not None:
            params_['max-age'] = max_age
            params_['expires'] = time.strftime('%a, %d-%b-%Y %T GMT', time.gmtime(time.time() + max_age))
        if not cookie_data:
            response.del_cookie(
                self._cookie_name,
                domain = params_['domain'],
                path = params_['path']
            )
        else:
            response.set_cookie(self._cookie_name, cookie_data, **params_)


