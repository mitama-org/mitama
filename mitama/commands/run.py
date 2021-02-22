#!/usr/bin/python
"""サーバー起動コマンド

ポート番号を引数に取ってHTTPサーバーを起動するコマンド
実行されてないマイグレーションもこいつが実行する
"""
import os
import sys
import importlib
from mitama.app import AppRegistry
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

        project_name = os.getcwd().split('/')[-1]
        sys.path.append(str(config._project_dir))
        project = importlib.import_module("__project__", package=".").__project__
        run_app(project, project.port)
