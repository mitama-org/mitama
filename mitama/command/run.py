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
        sys.path.append(str(config._project_dir))
        for app_name in config.apps:
            _app = config.apps[app_name]
            init = importlib.__import__(_app['include'], fromlist = ['init_app'])
            init.init_app(app_name)
            app = importlib.__import__(_app['include'] + '.main', fromlist=['app'])
            server.add_app(app.app, _app['path'])
        server.run()
