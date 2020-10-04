from mitama._extra import _Singleton
from mitama.app.router import Router
from mitama.app.method import group
from mitama.conf import get_from_project_dir
import sys
import os
import importlib
from watchdog.events import FileSystemEvent, PatternMatchingEventHandler
from watchdog.observers import Observer

class AppRegistry(_Singleton):
    '''稼働しているアプリのレジストリ

    サーバー内で稼働しているアプリのパスやパッケージ名が登録されているレジストリです。
    mitama.jsonを読み込んでアプリを起動するクラスでもあります。
    dictっぽくアプリの取得や配信の停止などが可能です。
    '''
    _map = dict()
    _server = None
    _router = None
    changed = False
    def __init__(self):
        super().__init__()
    def start_watch(self):
        observer = Observer()
        class Handler(PatternMatchingEventHandler):
            def on_event(self_):
                self.load_config()
            def on_created(self, event):
                self.on_event()
            def on_updated(self, event):
                self.on_event()
            def on_deleted(self, event):
                self.on_event()
        observer.schedule(Handler(), self.project_dir)
    def append(self, app):
        self._map.append(app)
    def __iter__(self):
        for app in self._map.values():
            yield app
    def __setitem__(self, path, app):
        self.changed = True
        self._map[path] = app
    def __getitem__(self, path):
        return self._map[path]
    def __delitem__(self, path):
        self.changed = True
        del self._map[path]
    def reset(self):
        '''アプリの一覧をリセットします'''
        self.changed = True
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
            if app_name not in sys.modules:
                init = importlib.__import__(app_name, fromlist=['AppBuilder'])
            else:
                init = importlib.reload(app_name)
            builder = init.AppBuilder()
            builder.set_package(app_name)
            builder.set_project_dir(config._project_dir / app_name)
            builder.set_project_root_dir(config._project_dir)
            builder.set_path(_app['path'])
            builder.set_name(app_name)
            app = builder.build()
            self[_app['path']] = app
    def router(self):
        '''アプリの情報に基づいてルーティングエンジンを生成します'''
        if self._router == None:
            router = Router()
            for k in self._map.keys():
                app = self._map[k]
                router.add_route(group(k, app))
            self._router = router
        elif self.changed:
            router = Router()
            for k in self._map.keys():
                app = self._map[k]
                router.add_route(group(k, app))
            self._router = router
            self.changed = False
        return self._router
