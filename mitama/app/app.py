#!/usr/bin/python
from aiohttp import web
from yarl import URL
from jinja2 import Environment, FileSystemLoader
from pathlib import Path
import magic
import os
from base64 import b64encode
from mitama.app.noimage import load_noimage_app
from mitama.hook import HookRegistry
from mitama.http import Request, Response

def dataurl(blob):
    f = magic.Magic(mime = True, uncompress = True)
    mime = f.from_buffer(blob)
    return 'data:'+mime+';base64,'+b64encode(blob).decode()

class App:
    template_dir = 'templates'
    instances = list()
    description = ""
    name = ""
    @property
    def icon(self):
        return load_noimage_app()
    def __init__(self, **kwargs):
        self.app = web.Application(client_max_size = kwargs["client_max_size"] if "client_max_size" in kwargs else 100*1024*1024)
        self.screen_name = kwargs['name']
        self.path = kwargs['path']
        self.project_dir = Path(kwargs['project_dir']) if 'project_dir' in kwargs else None
        self.project_root_dir = Path(kwargs['project_root_dir']) if 'project_dir' in kwargs else None
        self.install_dir = Path(kwargs['install_dir']) if 'project_dir' in kwargs else Path(os.path.dirname(__file__)) / '../http/'
        for instance in self.instances:
            instance.app = self
            instance.view = self.view
            if hasattr(instance,  '__connected__'):
                instance.__connected__()
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
        async def handle(request):
            if not isinstance(request, Request):
                request = Request.from_request(request)
            result = await self.router.match(request)
            if result:
                request, handle = result
                return await handle(request)
            else:
                return await self.error(request, 404)
        self.app.router.add_route('*', '/{tail:.*}', handle)
    def __getattr__(self, name):
        return getattr(self.app, name)
    def set_middleware(self, middlewares):
        self.app.middlewares.extend(middlewares)
    def convert_fullurl(self, req, url):
        scheme= req.scheme
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
        url = str(url.path)
        url = URL(url[len(path):])
        return url
    @property
    def view(self):
        self._view= Environment(
            enable_async = True,
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
    async def error(self, request, code):
        template = self.view.get_template(str(code) + '.html')
        return await Response.render(template, request)
