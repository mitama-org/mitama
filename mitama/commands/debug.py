#!/usr/bin/python
"""サーバー起動コマンド

ポート番号を引数に取ってHTTPサーバーを起動するコマンド
実行されてないマイグレーションもこいつが実行する
"""
import mitama.models
from mitama.app import AppRegistry, _MainApp
from mitama.app.http import run_app
from mitama.conf import get_from_project_dir


class Command:
    def handle(self, argv=None):
        config = get_from_project_dir()
        try:
            port = argv[0]
        except IndexError:
            if hasattr(config, "port"):
                port = config.port
            else:
                port = "8080"
        if not hasattr(config, "ssl"):
            config.ssl = False
        app_registry = AppRegistry()
        app_registry.load_config()
        app = _MainApp(app_registry)
        app_registry.start_watch()
        run_app(app, port)
