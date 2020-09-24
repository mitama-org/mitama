from mitama.extra import _Singleton
from mitama.app.router import Router
from mitama.conf import get_from_project_dir
import sys
import os
import importlib

class AppRegistry(_Singleton):
    _map = dict()
    _server = None
    def append(self, app):
        self._map.append(app)
    def __iter__(self):
        for app in self._map.values():
            yield app
    def __setitem__(self, path, app):
        self._map[path] = app
    def __getitem__(self, path):
        return self._map[path]
    def __delitem__(self, path):
        del self._map[path]
    def reset(self):
        self._map = dict()
    def load_config(self):
        config = get_from_project_dir()
        sys.path.append(str(config._project_dir))
        for app_name in config.apps:
            _app = config.apps[app_name]
            init = importlib.__import__(app_name, fromlist = ['init_app'])
            builder = init.AppBuilder()
            app_dir = config._project_dir / app_name
            if not app_dir.is_dir():
                os.mkdir(app_dir)
            builder.set_project_dir(config._project_dir / app_name)
            builder.set_project_root_dir(config._project_dir)
            builder.set_path(_app['path'])
            builder.set_name(app_name)
            app = builder.build()
            self[_app['path']] = app
        if self._server != None:
            self._server.router = self.router()
    def router(self):
        router = Router()
        for k in self._map.keys():
            app_router = self._map[k].router.clone(prefix = k)
            router.add_route(app_router)
        return router
