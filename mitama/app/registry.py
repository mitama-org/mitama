from mitama.extra import _Singleton
from mitama.app.router import Router
from mitama.conf import get_from_project_dir
import sys
import os
import importlib

class AppRegistry(_Singleton):
    '''稼働しているアプリのレジストリ

    サーバー内で稼働しているアプリのパスやパッケージ名が登録されているレジストリです。
    mitama.jsonを読み込んでアプリを起動するクラスでもあります。
    dictっぽくアプリの取得や配信の停止などが可能です。
    '''
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
        '''アプリの一覧をリセットします'''
        self._map = dict()
    def load_config(self):
        '''アプリの一覧をmitama.jsonから読み込み、配信します'''
        config = get_from_project_dir()
        sys.path.append(str(config._project_dir))
        for app_name in config.apps:
            _app = config.apps[app_name]
            app_dir = config._project_dir / app_name
            if not app_dir.is_dir():
                os.mkdir(app_dir)
            init = importlib.__import__(app_name, fromlist = ['init_app'])
            builder = init.AppBuilder()
            builder.set_project_dir(config._project_dir / app_name)
            builder.set_project_root_dir(config._project_dir)
            builder.set_path(_app['path'])
            builder.set_name(app_name)
            app = builder.build()
            self[_app['path']] = app
        if self._server != None:
            self._server.load_routes()
    def router(self):
        '''アプリの情報に基づいてルーティングエンジンを生成します'''
        router = Router()
        for k in self._map.keys():
            app_router = self._map[k].router.clone(prefix = k)
            router.add_route(app_router)
        return router
