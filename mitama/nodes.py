#!/usr/bin/python
'''ノード定義

    * UserとGroupのモデル定義を書きます。
    * 関係テーブルのモデル実装は別モジュールにしようかと思ってる
    * sqlalchemyのベースクラスを拡張したNodeクラスに共通のプロパティを載せて、そいつらをUserとGroupに継承させてます。

Todo:
    * sqlalchemy用にUser型とGroup型を作って、↓のクラスをそのまま使ってDB呼び出しできるようにしたい
'''

from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from mitama.db import types

Base = declarative_base()

class Node:
    pass

class User(Base, Node):
    __tablename__ = 'mitama_user'
    id = Column(Integer, primary_key = True)
    name = Column(String(255))
    screen_name = Column(String(255))
    password = Column(String(255))

class Group(Base, Node):
    __tablename__ = 'mitama_group'
    id = Column(Integer, primary_key = True)
    name = Column(String(255))
    screen_name = Column(String(255))

