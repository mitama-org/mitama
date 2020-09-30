#!/usr/bin/python
'''サーバー起動コマンド
    * ポート番号を引数に取ってHTTPサーバーを起動するコマンド
    * 実行されてないマイグレーションもこいつが実行する

Todo:
    * マイグレーションの実行の実装

'''
from mitama.http.server import Server
import mitama.nodes
from mitama.app import AppRegistry

class Command:
    def handle(self, argv = None):
        try:
            port = argv[0]
        except IndexError:
            port = '8080'
        server = Server(port)
        registry = AppRegistry()
        registry.load_config()
        server.registry(registry)
        server.run()
