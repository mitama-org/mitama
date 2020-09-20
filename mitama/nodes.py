#!/usr/bin/python
'''ノード定義

    * UserとGroupのモデル定義を書きます。
    * 関係テーブルのモデル実装は別モジュールにしようかと思ってる
    * sqlalchemyのベースクラスを拡張したNodeクラスに共通のプロパティを載せて、そいつらをUserとGroupに継承させてます。

Todo:
    * sqlalchemy用にUser型とGroup型を作って、↓のクラスをそのまま使ってDB呼び出しできるようにしたい
'''

from sqlalchemy.ext.declarative import declarative_base
from mitama.db import _CoreDatabase, func, orm
from mitama.db.types import Column, Integer, String, Node, Group, LargeBinary
from mitama.hook import HookRegistry
import magic
from base64 import b64encode

db = _CoreDatabase()
hook_registry = HookRegistry()

class Relation(db.Model):
    __tablename__ = 'mitama_relation'
    id = Column(Integer, primary_key = True)
    parent = Column(Group)
    child = Column(Node)

class Node(object):
    id = Column(Integer, primary_key = True)
    icon = Column(LargeBinary)
    name = Column(String(255))
    screen_name = Column(String(255))
    @classmethod
    def retrieve(cls, id = None, screen_name = None):
        if id != None:
            node = cls.query.filter(cls.id == id).first()
        elif screen_name != None:
            node = cls.query.filter(cls.screen_name == screen_name).first()
        else:
            raise Exception('')
        return node
    def icon_to_dataurl(self):
        f = magic.Magic(mime = True, uncompress = True)
        mime = f.from_buffer(self.icon)
        return 'data:'+mime+';base64,'+b64encode(self.icon).decode()
    def parents(self):
        rels = Relation.query.filter(Relation.child == self).all()
        parent = list()
        for rel in rels:
            parent.append(rel.parent)
        return parent
    def is_ancester(self, node):
        if node.__class__.__name__ != 'Group' and node.__class__.__name__ != 'User':
            raise TypeError('Checking object must be Group or User instance')
        layer = self.parents()
        while len(layer) > 0:
            if node in layer:
                return True
            layer_ = list()
            for node_ in layer:
                layer_.extend(
                    node_.parents()
                )
            layer = layer_
        return False

class User(db.Model, Node):
    __tablename__ = 'mitama_user'
    password = Column(String(255))
    def delete(self):
        hook_registry.delete_user(self)
        super().delete()
    def update(self):
        super().update()
        hook_registry.update_user(self)
    def create(self):
        super().create()
        hook_registry.create_user(self)

class Group(db.Model, Node):
    __tablename__ = 'mitama_group'
    @classmethod
    def tree(cls):
        noparent = [rel.child.id for rel in db.session.query(Relation.child).group_by(Relation.child) if rel.child.__class__.__name__ == "Group"]
        groups = [group for group in Group.query.filter().all() if group.id not in noparent and group.__class__.__name__ == "Group"]
        return groups
    def append(self, node):
        if node.__class__.__name__ != 'Group' and node.__class__.__name__ != 'User':
            raise TypeError('Appending object must be Group or User instance')
        rel = Relation()
        rel.parent = self
        rel.child = node
        rel.create()
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
    def is_descendant(self, node):
        if node.__class__.__name__ != 'Group' and node.__class__.__name__ != 'User':
            raise TypeError('Checking object must be Group or User instance')
        layer = self.children()
        while len(layer) > 0:
            if node in layer:
                return True
            layer_ = list()
            for node_ in layer:
                if node_.__class__.__name__ == 'Group':
                    layer_.extend(
                        node_.children()
                    )
            layer = layer_
        return False
    def is_in(self, node):
        if node.__class__ != 'Group' and node.__class__ != 'User':
            raise TypeError('Checking object must be Group or User instance')
        rels = Relation.query.filter(Relation.parent == self and Relation.node == node).all()
        return rels.len()!=0
    def delete(self):
        hook_registry.delete_group(self)
        super().delete()
    def update(self):
        super().update()
        hook_registry.update_group(self)
    def create(self):
        super().create()
        hook_registry.create_group(self)



db.create_all()
