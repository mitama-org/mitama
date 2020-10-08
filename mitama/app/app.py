#!/usr/bin/python
from yarl import URL
from jinja2 import Environment, FileSystemLoader
from pathlib import Path
import magic
import os
from base64 import b64encode
from mitama.noimage import load_noimage_app
from mitama.hook import HookRegistry
from mitama.http import Request, Response

def dataurl(blob):
    f = magic.Magic(mime = True, uncompress = True)
    mime = f.from_buffer(blob)
    return 'data:'+mime+';base64,'+b64encode(blob).decode()

class App:
    template_dir = 'templates'
    description = ""
    name = ""
    @property
    def icon(self):
        return load_noimage_app()
    def __init__(self, **kwargs):
        self.screen_name = kwargs['name']
        self.path = kwargs['path']
        self.package = kwargs['package']
        self.project_dir = Path(kwargs['project_dir']) if 'project_dir' in kwargs else None
        self.project_root_dir = Path(kwargs['project_root_dir']) if 'project_dir' in kwargs else None
        self.install_dir = Path(kwargs['install_dir']) if 'project_dir' in kwargs else Path(os.path.dirname(__file__)) / '../http/'
        self.router._app = self
        hook_registry = HookRegistry()
        if hasattr(self, 'create_user'):
            hook_registry.add_create_user_hook(self.create_user)
        if hasattr(self, 'create_group'):
            hook_registry.add_create_group_hook(self.create_group)
        if hasattr(self, 'update_user'):
            hook_registry.add_update_user_hook(self.update_user)
        if hasattr(self, 'update_group'):
            hook_registry.add_update_group_hook(self.update_group)
        if hasattr(self, 'delete_user'):
            hook_registry.add_delete_user_hook(self.delete_user)
        if hasattr(self, 'delete_group'):
            hook_registry.add_delete_group_hook(self.delete_group)
    def __call__(self, request):
        if not isinstance(request, Request):
            request = Request.from_request(request)
        result = self.router.match(request)
        if result:
            request, handle, method = result
            return handle(request)
        else:
            return self.error(request, 404)
    def set_middleware(self, middlewares):
        self.app.middlewares.extend(middlewares)
    def convert_fullurl(self, req, url):
        scheme = req.scheme
        hostname = req.host
        path = self.path
        if path[0] != '/':
            path = '/' + path
        if path[-1] == '/':
            path = path[0:-2]
        if url[0] != '/':
            url = '/' + url
        return scheme + "://" + hostname + path + url
    def convert_url(self, url):
        path = self.path
        if path[0] != '/':
            path = '/' + path
        if path[-1] == '/':
            path = path[0:-2]
        if url[0] != '/':
            url = '/' + url
        return path + url
    def revert_url(self, url):
        path = self.path
        if path[0] != '/':
            path = '/' + path
        if path[-1] == '/':
            path = path[0:-2]
        url = str(url)
        url = url[len(path):]
        return url
    @property
    def view(self):
        self._view= Environment(
            loader = FileSystemLoader(self.install_dir / self.template_dir)
        )
        def filter_user(arg):
            return [user for user in arg if user.__class__.__name__ == "User"]
        def filter_group(arg):
            return [group for group in arg if group.__class__.__name__ == "Group"]
        self._view.filters["user"] = filter_user
        self._view.filters["group"] = filter_group
        self._view.globals.update(
            url = self.convert_url,
            fullurl = self.convert_fullurl,
            dataurl = dataurl
        )
        return self._view
    def error(self, request, code):
        template = self.view.get_template(str(code) + '.html')
        return Response.render(template)
    def match(self, request):
        result = self.router.match(request)
        if result == False:
            return False
        else:
            request, handle, method = self.router.match(request)
            def _handle(request):
                request.app = self
                return handle(request)
            return request, _handle, method

def _session_middleware():
    from mitama.http.session import EncryptedCookieStorage
    from cryptography import fernet
    from mitama.app import Middleware
    import base64
    class SessionMiddleware(Middleware):
        fernet_key = fernet.Fernet.generate_key()
        def __init__(self):
            secret_key = base64.urlsafe_b64decode(self.fernet_key)
            cookie_storage = EncryptedCookieStorage(secret_key)
            self.storage = cookie_storage
        def process(self, request, handler):
            request['mitama_session_storage'] = self.storage
            raise_response = False
            response = handler(request)
            if not isinstance(response, Response):
                return response
            session = request.get('mitama_session')
            if session is not None:
                if session._changed:
                    self.storage.save_session(request, response, session)
            if raise_response:
                raise response
            return response
    return SessionMiddleware

class _MainApp(App):
    def __init__(self, app_registry):
        self.app_registry = app_registry
        self._router = None
        super().__init__(name='_mitama', path='/', package = '_mitama')
    @property
    def router(self):
        if self._router == None or self.app_registry.changed:
            router = self.app_registry.router()
            router.add_middleware(_session_middleware())
            self._router = router
        return self._router
