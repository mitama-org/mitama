#!/usr/bin/python
'''ノード定義

    * UserとGroupのモデル定義を書きます。
    * 関係テーブルのモデル実装は別モジュールにしようかと思ってる
    * sqlalchemyのベースクラスを拡張したNodeクラスに共通のプロパティを載せて、そいつらをUserとGroupに継承させてます。

Todo:
    * sqlalchemy用にUser型とGroup型を作って、↓のクラスをそのまま使ってDB呼び出しできるようにしたい
'''

from sqlalchemy.ext.declarative import declarative_base
from mitama.db import _CoreDatabase, Column, Integer, String

db = _CoreDatabase()

class User(db.Model):
    __tablename__ = 'mitama_user'
    id = Column(Integer, primary_key = True)
    name = Column(String(255))
    screen_name = Column(String(255))
    password = Column(String(255))

class Group(db.Model):
    __tablename__ = 'mitama_group'
    id = Column(Integer, primary_key = True)
    name = Column(String(255))
    screen_name = Column(String(255))

