#!/usr/bin/python
'''ノード定義

    * UserとGroupのモデル定義を書きます。
    * 関係テーブルのモデル実装は別モジュールにしようかと思ってる
    * sqlalchemyのベースクラスを拡張したNodeクラスに共通のプロパティを載せて、そいつらをUserとGroupに継承させてます。

Todo:
    * sqlalchemy用にUser型とGroup型を作って、↓のクラスをそのまま使ってDB呼び出しできるようにしたい
'''

from sqlalchemy.ext.declarative import declarative_base
from mitama.db import _CoreDatabase
from mitama.db.types import Column, Integer, String

db = _CoreDatabase()

class User(db.Model):
    __tablename__ = 'mitama_user'
    id = Column(Integer, primary_key = True)
    name = Column(String(255))
    screen_name = Column(String(255))
    password = Column(String(255))
    @staticmethod
    def retrieve(id = None, screen_name = None):
        if id != None:
            user = User.query.filter(User.id == id).first()
        elif screen_name != None:
            user = User.query.filter(User.screen_name == screen_name).first()
        else:
            raise Exception()
        return user


class Group(db.Model):
    __tablename__ = 'mitama_group'
    id = Column(Integer, primary_key = True)
    name = Column(String(255))
    screen_name = Column(String(255))
    @staticmethod
    def retrieve(id = None, screen_name = None):
        if id != None:
            group = Group.query.filter(Group.id == id).first()
        elif screen_name != None:
            group = Group.query.filter(Group.screen_name == screen_name).first()
        else:
            raise Exception()
        return group

