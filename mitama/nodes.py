#!/usr/bin/python
'''ノード定義

    * UserとGroupのモデル定義を書きます。
    * 関係テーブルのモデル実装は別モジュールにしようかと思ってる
    * sqlalchemyのベースクラスを拡張したNodeクラスに共通のプロパティを載せて、そいつらをUserとGroupに継承させてます。

Todo:
    * sqlalchemy用にUser型とGroup型を作って、↓のクラスをそのまま使ってDB呼び出しできるようにしたい
'''

import sqlalchemy
from sqlalchemy.ext.declarative import declarative_base
from mitama.db import types

Base = declarative_base()

class Node(Base):
    id = Column(Interger, primary_key = True)
    name = Column(String(255))
    screen_name = Column(String(255))

class User(Node):
    __tablename__ = 'mitama_user'
    password = Column(String(255))

class Group(Node):
    __tablename__ = 'mitama_group'

