import importlib
import os
import sys
from pathlib import Path
import json

from watchdog.events import FileSystemEvent, PatternMatchingEventHandler
from watchdog.observers import Observer

from mitama._extra import _Singleton
from mitama.conf import get_from_project_dir

from .method import group
from .router import Router


class AppRegistry(_Singleton):
    """稼働しているアプリのレジストリ

    サーバー内で稼働しているアプリのパスやパッケージ名が登録されているレジストリです。
    mitama.jsonを読み込んでアプリを起動するクラスでもあります。
    dictっぽくアプリの取得や配信の停止などが可能です。
    """

    _map = dict()
    _server = None
    _router = None

    def __init__(self):
        super().__init__()

    def __iter__(self):
        for app in self._map.values():
            yield app

    def __setitem__(self, app_name, app):
        app.project = self.project
        self._map[app_name] = app

        def sorter(x):
            x_ = x[1].path
            if x_[-1] != "/":
                x_ += "/"
            return -1 * len(x_.split('/'))

        self._map = dict(
            sorted(
                self._map.items(),
                key=sorter
            )
        )

    def __getitem__(self, app_name):
        return self._map[app_name]

    def __delitem__(self, app_name):
        del self._map[app_name]

    def reset(self):
        """アプリの一覧をリセットします"""
        self._map = dict()

    def load_package(self, package, screen_name=None, path="/"):
        project_dir = self.project.project_dir
        if str(project_dir) not in sys.path:
            sys.path.append(str(project_dir))
        if app_name not in sys.modules:
            init = importlib.__import__(app_name, fromlist=["AppBuilder"])
        else:
            init = importlib.reload(app_name)
        builder = init.AppBuilder()
        if screen_name is None:
            screen_name = package
        builder.set_package(package)
        builder.set_screen_name(screen_name)
        builder.set_project_root_dir(project_dir)
        builder.set_project_dir(project_dir / screen_name)
        builder.set_path(path)
        app = builder.build()
        return app

    def router(self):
        """アプリの情報に基づいてルーティングエンジンを生成します"""
        if self._router == None:
            router = Router(
                middlewares=[_session_middleware()]
            )
            for app in self:
                router.add_route(group(app.path, app))
            self._router = router
        return self._router

