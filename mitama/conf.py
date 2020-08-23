#!/usr/bin/python
'''configの実装

    * 柔軟性を上げたかったので、デフォルト値を持ったオブジェクトのプロパティをdictの値で更新する方式をとった
    * とりあえず、プロジェクトフォルダ直下のmitama.jsonを読む仕様にしている。

Todo:
    * コマンドから生成するmitama.jsonの値はconfigのデフォルト値を使うので、mitama.conf.Configにエクスポート関数を用意したい
'''

import os
from pathlib import Path
import json

class Config:
    apps = dict()
    def __init__(self, path, dic):
        self._project_dir = path;
        self._sqlite_db_path = Path(self._project_dir) / 'db.sqlite3'
        for k in dic:
            try:
                setattr(self, k, dic[k])
            except:
                continue
    def to_dict(self):
        # dictに変換する
        dic = dict()
        for k in self.__dict__:
            if k[0] != '_':  #__dict__では_Configプレフィクスがつくので、その文字数を避けてる
                dic[k] = self.__dict__[k]
        return dic


def get_from_project_dir():
    path = Path(os.getcwd())
    with open(path / 'mitama.json') as f:
        data = f.read()
    return Config(path, json.loads(data))
