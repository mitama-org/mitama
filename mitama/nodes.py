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
from mitama.db.types import Column, Integer, String, Node, Group

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

class Relation(db.Model):
    __tablename__ = 'mitama_relation'
    id = Column(Integer, primary_key = True)
    parent = Column(Group)
    child = Column(Node)

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
            raise Exception('')
        return group
    def append(self, node):
        if node.__class__.__name__ != 'Group' and node.__class__.__name__ != 'User':
            raise TypeError('Appending object must be Group or User instance')
        rel = Relation()
        rel.parent = self
        rel.child = node
        db.session.add(rel)
        db.session.commit()
    def append_all(self, nodes):
        for node in nodes:
            if node.__class__.__name__ != 'Group' and node.__class__.__name__ != 'User':
                raise TypeError('Appending object must be Group or User instance')
            rel = Relation()
            rel.parent = self
            rel.child = node
            db.session.add(rel)
        db.session.commit()
    def remove(self, node):
        if node.__class__.__name__ != 'Group' and node.__class__.__name__ != 'User':
            raise TypeError('Removing object must be Group or User instance')
        rel = Relation.query.filter(Relation.parent == self and Relation.child == node).first()
        db.session.delete(rel)
        db.session.commit()
    def remove_all(self, nodes):
        for node in nodes:
            if node.__class__.__name__ != 'Group' and node.__class__.__name__ != 'User':
                raise TypeError('Appending object must be Group or User instance')
        rels = Relation.query.filter(Relation.parent == self and Relation.child in nodes).all()
        db.session.delete(rels)
        db.session.commit()
    def children(self):
        rels = Relation.query.filter(Relation.parent == self).all()
        children = list()
        for rel in rels:
            children.append(rel.child)
        return children
    def is_in(self, node):
        if node.__class__ != 'Group' and node.__class__ != 'User':
            raise TypeError('Removing object must be Group or User instance')
        rels = Relation.query.filter(Relation.parent == self and Relation.node == node).all()
        return rels.len()!=0
