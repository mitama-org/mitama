#!/usr/bin/python
'''サーバー起動コマンド

ポート番号を引数に取ってHTTPサーバーを起動するコマンド
実行されてないマイグレーションもこいつが実行する
'''
from mitama.http import run_app
import mitama.nodes
from mitama.app import _MainApp, AppRegistry

class Command:
    def handle(self, argv = None):
        try:
            port = argv[0]
        except IndexError:
            port = '8080'
        app_registry = AppRegistry()
        app_registry.load_config()
        app = _MainApp(app_registry)
        app_registry.start_watch()
        run_app(app, port)