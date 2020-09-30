#!/usr/bin/python
'''コマンド定義

    * 1ファイル1コマンドでクラスとして書いてます
    * handleがコマンドライン引数の引数部を受け取って実行する
    * 抽象化はするかどうか迷ってる（Pythonで抽象化がどれくらい尊いものかよくわかんない）
    * argparseを入れようか迷ったけど、位置引数しか必要に成る予定が無いのでとりあえず入れてない
'''

import importlib
import sys

def exec():
    '''コマンドを起動します

    コマンドライン引数からサブコマンドのインスタンスを生成し、起動します。
    '''
    subcmd = sys.argv[1]
    if subcmd == '':
        subcmd = 'help'
    m = importlib.import_module('.' + subcmd, 'mitama.command')
    cmd = m.Command()
    cmd.handle(sys.argv[2:])

