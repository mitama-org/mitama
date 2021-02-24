#!/usr/bin/python
"""コマンド定義

    * 1ファイル1コマンドでクラスとして書いてます
    * handleがコマンドライン引数の引数部を受け取って実行する
    * 抽象化はするかどうか迷ってる（Pythonで抽象化がどれくらい尊いものかよくわかんない）
    * argparseを入れようか迷ったけど、位置引数しか必要に成る予定が無いのでとりあえず入れてない
"""

import argparse
import mitama.commands

parser = argparse.ArgumentParser(description="Mitama command utilities")
subparser = parser.add_subparsers()

init = subparser.add_parser("init", help="Initialize directory as a Mitama project")
init.set_defaults(handler=commands.init)

new = subparser.add_parser("new", help="Create new Mitama project directory")
new.set_defaults(handler=commands.new)

mkapp = subparser.add_parser("mkapp", help="Create new Mitam application")
mkapp.set_defaults(handler=commands.mkapp)

version = subparser.add_parser("version", help="Check version code")
version.set_defaults(handler=commands.version)

def command_exec():
    """コマンドを起動します

    コマンドライン引数からサブコマンドのインスタンスを生成し、起動します。
    """
    args = parser.parse_args()
    args.handler(args)
