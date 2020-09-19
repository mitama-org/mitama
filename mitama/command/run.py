#!/usr/bin/python
'''サーバー起動コマンド
    * ポート番号を引数に取ってHTTPサーバーを起動するコマンド
    * 実行されてないマイグレーションもこいつが実行する

Todo:
    * マイグレーションの実行の実装

'''
from mitama.conf import get_from_project_dir
from mitama.http.server import Server
import mitama.nodes
from mitama.app import AppRegistry
import os
import sys
import importlib

class Command:
    def handle(self, argv = None):
        try:
            port = argv[0]
        except IndexError:
            port = '8080'
        server = Server(port)
        config = get_from_project_dir()
        registry = AppRegistry()
        sys.path.append(str(config._project_dir))
        for app_name in config.apps:
            _app = config.apps[app_name]
            init = importlib.__import__(app_name, fromlist = ['init_app'])
            builder = init.AppBuilder()
            app_dir = config._project_dir / app_name
            if not app_dir.is_dir():
                os.mkdir(app_dir)
            builder.set_project_dir(config._project_dir / app_name)
            builder.set_path(_app['path'])
            builder.set_name(app_name)
            app = builder.build()
            server.add_app(app.app, _app['path'])
            registry.append(app)
        server.run()
