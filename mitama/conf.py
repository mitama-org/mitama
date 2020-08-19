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
    project_dir = os.path.dirname(__file__)
    sqlite_db_path = Path(project_dir) / 'db.sqlite3'
    apps = dict()
    def __init__(self, dic):
        for k in dic:
            try:
                setattr(self, k, dic[k])
            except:
                continue
    def to_dict(self):
        # dictに変換する
        return { }


def get_from_project_dir():
    path = Path(os.path.dirname(__file__))
    with open(path / 'mitama.conf') as f:
        data = f.read()
    return Config(json.loads(data))
