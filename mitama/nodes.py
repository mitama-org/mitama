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
from mitama.noimage import load_noimage_user, load_noimage_group

db = _CoreDatabase()
hook_registry = HookRegistry()

class Relation(db.Model):
    parent = Column(Group)
    child = Column(Node)

class Node(object):
    _icon = Column(LargeBinary)
    name = Column(String(255))
    screen_name = Column(String(255))
    @property
    def id(self):
        return self._id
    @classmethod
    def retrieve(cls, id = None, screen_name = None):
        if id != None:
            node = cls.query.filter(cls._id == id).first()
        elif screen_name != None:
            node = cls.query.filter(cls.screen_name == screen_name).first()
        else:
            raise Exception('')
        return node
    def icon_to_dataurl(self):
        f = magic.Magic(mime = True, uncompress = True)
        mime = f.from_buffer(self._icon)
        return 'data:'+mime+';base64,'+b64encode(self.icon).decode()
    def parents(self):
        rels = Relation.query.filter(Relation.child == self).all()
        parent = list()
        for rel in rels:
            parent.append(rel.parent)
        return parent
    def is_ancestor(self, node):
        if not isinstance(node, Group) and not isinstance(node, User):
            raise TypeError('Checking object must be Group or User instance')
        layer = self.parents()
        while len(layer) > 0:
            if isinstance(node, Group) and node in layer:
                return True
            else:
                for node_ in layer:
                    if isinstance(node, User) and node_.is_in(node):
                        return True
            layer_ = list()
            for node_ in layer:
                layer_.extend(
                    node_.parents()
                )
            layer = layer_
        return False

class User(Node, db.Model):
    '''ユーザーのモデルクラスです

    :param _id: 固有のID
    :param screen_name: ログイン名
    :param name: 名前
    :param password: パスワード
    :param icon: アイコン
    '''
    __tablename__ = 'mitama_user'
    password = Column(String(255))
    @property
    def icon(self):
        if self._icon != None:
            return self._icon
        else:
            return load_noimage_user()
    @icon.setter
    def icon(self, value):
        self._icon = value
    def delete(self):
        '''ユーザーを削除します'''
        hook_registry.delete_user(self)
        super().delete()
    def update(self):
        '''ユーザー情報を更新します'''
        super().update()
        hook_registry.update_user(self)
    def create(self):
        '''ユーザーを作成します'''
        super().create()
        hook_registry.create_user(self)

class Group(Node, db.Model):
    '''グループのモデルクラスです

    :param _id: 固有のID
    :param screen_name: ドメイン名
    :param name: 名前
    :param icon: アイコン
    '''
    __tablename__ = 'mitama_group'
    @property
    def icon(self):
        if self._icon != None:
            return self._icon
        else:
            return load_noimage_group()
    @icon.setter
    def icon(self, value):
        self._icon = value
    @classmethod
    def tree(cls):
        noparent = [rel.child._id for rel in db.session.query(Relation.child).group_by(Relation.child) if isinstance(rel.child, Group)]
        groups = [group for group in Group.query.filter().all() if group._id not in noparent and isinstance(group, Group)]
        return groups
    def append(self, node):
        if not isinstance(node, Group) and not isinstance(node, User):
            raise TypeError('Appending object must be Group or User instance')
        rel = Relation()
        rel.parent = self
        rel.child = node
        rel.create()
    def append_all(self, nodes):
        for node in nodes:
            if not isinstance(node, Group) and not isinstance(node, User):
                raise TypeError('Appending object must be Group or User instance')
            rel = Relation()
            rel.parent = self
            rel.child = node
            Relation.query.session.add(rel)
        Relation.query.session.commit()
    def remove(self, node):
        if not isinstance(node, Group) and not isinstance(node, User):
            raise TypeError('Removing object must be Group or User instance')
        rel = Relation.query.filter(Relation.parent == self).filter(Relation.child == node).first()
        rel.delete()
    def remove_all(self, nodes):
        for node in nodes:
            if not isinstance(node, Group) and not isinstance(node, User):
                raise TypeError('Appending object must be Group or User instance')
        rels = Relation.query.filter(Relation.parent == self).filter(Relation.child in nodes).all()
        Relation.query.session.delete(rels)
        Relation.query.session.commit()
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
        if not isinstance(node, Group) and not isinstance(node, User):
            raise TypeError('Checking object must be Group or User instance')
        rels = Relation.query.filter(Relation.parent == self).filter(Relation.child == node).all()
        return len(rels) != 0
    def delete(self):
        '''グループを削除します'''
        hook_registry.delete_group(self)
        super().delete()
    def update(self):
        '''グループの情報を更新します'''
        super().update()
        hook_registry.update_group(self)
    def create(self):
        '''グループを作成します'''
        super().create()
        hook_registry.create_group(self)



db.create_all()
