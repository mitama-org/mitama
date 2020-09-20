#!/usr/bin/python
from aiohttp import web
from yarl import URL
from jinja2 import Environment, FileSystemLoader
from pathlib import Path
import magic
from base64 import b64encode

class App:
    template_dir = 'templates';
    def __init__(self, **kwargs):
        kwargs['middlewares'] = [
            web.normalize_path_middleware(append_slash = True)
        ]
        self.app = web.Application()
        self.name = kwargs['name']
        self.path = kwargs['path']
        self.project_dir = Path(kwargs['project_dir'])
        self.install_dir = Path(kwargs['install_dir'])
        self.view= Environment(
            enable_async = True,
            loader = FileSystemLoader(self.install_dir / self.template_dir)
        )
        def dataurl(blob):
            f = magic.Magic(mime = True, uncompress = True)
            mime = f.from_buffer(blob)
            return 'data:'+mime+';base64,'+b64encode(blob).decode()
        def filter_user(arg):
            return [user for user in arg if user.__class__.__name__ == "User"]
        def filter_group(arg):
            return [group for group in arg if group.__class__.__name__ == "Group"]
        self.view.filters["user"] = filter_user
        self.view.filters["group"] = filter_group
        self.view.globals.update(
            uri = self.convert_uri,
            fulluri = self.convert_fulluri,
            dataurl = dataurl
        )
        for instance in self.instances:
            instance.app = self
            instance.view = self.view
            if hasattr(instance,  '__connected__'):
                instance.__connected__()
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
        if callable(self.router):
            router = self.router()
        else:
            router = self.router
        self.app.router.add_route('*', '/{tail:(?!login|logout).*}', router.match)
    def __getattr__(self, name):
        return getattr(self.app, name)
    def set_middleware(self, middlewares):
        self.app.middlewares.extend(middlewares)
    def convert_fulluri(self, req, uri):
        scheme= req.scheme
        hostname = req.host
        path = self.path
        if path[0] != '/':
            path = '/' + path
        if path[-1] == '/':
            path = path[0:-2]
        if uri[0] != '/':
            uri = '/' + uri
        return scheme + "://" + hostname + path + uri
    def convert_uri(self, uri):
        path = self.path
        if path[0] != '/':
            path = '/' + path
        if path[-1] == '/':
            path = path[0:-2]
        if uri[0] != '/':
            uri = '/' + uri
        return path + uri
    def revert_uri(self, uri):
        path = self.path
        if path[0] != '/':
            path = '/' + path
        if path[-1] == '/':
            path = path[0:-2]
        uri = str(uri.path)
        url = URL(uri[len(path):])
        return url
