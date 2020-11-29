#!/usr/bin/python
"""ノード定義

    * UserとGroupのモデル定義を書きます。
    * 関係テーブルのモデル実装は別モジュールにしようかと思ってる
    * sqlalchemyのベースクラスを拡張したNodeクラスに共通のプロパティを載せて、そいつらをUserとGroupに継承させてます。

Todo:
    * sqlalchemy用にUser型とGroup型を作って、↓のクラスをそのまま使ってDB呼び出しできるようにしたい
"""

import base64
import hashlib
import random
import secrets

import bcrypt
import jwt
import magic
from sqlalchemy.ext.declarative import declarative_base, declared_attr
from sqlalchemy.schema import UniqueConstraint

from mitama.app.hook import HookRegistry
from mitama.db import _CoreDatabase, func, orm
from mitama.db.types import Column, Group, Integer, LargeBinary
from mitama.db.types import Node as NodeType
from mitama.db.types import String
from mitama.noimage import load_noimage_group, load_noimage_user
from mitama.conf import get_from_project_dir

db = _CoreDatabase()
hook_registry = HookRegistry()

secret = secrets.token_hex(32)


class AuthorizationError(Exception):
    pass


class Relation(db.Model):
    parent = Column(Group)
    child = Column(NodeType)


class Node(object):
    _icon = Column(LargeBinary)
    _name = Column("name", String(255))
    _screen_name = Column("screen_name", String(255))
    _name_proxy = list()
    _screen_name_proxy = list()
    _icon_proxy = list()

    @property
    def id(self):
        return self._id

    @property
    def name(self):
        name = self._name
        for fn in self._name_proxy:
            name = fn(name)
        return name

    @property
    def screen_name(self):
        screen_name = self._screen_name
        for fn in self._screen_name_proxy:
            screen_name = fn(screen_name)
        return screen_name

    def to_dict(self):
        return {
            "_id": self._id,
            "name": self.name,
            "screen_name": self.screen_name,
        }

    @property
    def icon(self):
        if self._icon != None:
            icon = self._icon
        else:
            icon = self.load_noimage()
        for fn in self._icon_proxy:
            icon = fn(icon)
        return icon

    @name.setter
    def name(self, value):
        self._name = value

    @screen_name.setter
    def screen_name(self, value):
        self._screen_name = value

    @icon.setter
    def icon(self, value):
        self._icon = value

    @classmethod
    def retrieve(cls, id=None, screen_name=None):
        if id != None:
            node = cls.query.filter(cls._id == id).first()
        elif screen_name != None:
            node = cls.query.filter(cls._screen_name == screen_name).first()
        else:
            raise Exception("")
        return node

    """
    def __eq__(self, op):
        try:
            return self._id == op._id
        except:
            return False
    """

    def icon_to_dataurl(self):
        f = magic.Magic(mime=True, uncompress=True)
        mime = f.from_buffer(self.icon)
        return "data:" + mime + ";base64," + base64.b64encode(self.icon).decode()

    def parents(self):
        rels = Relation.query.filter(Relation.child == self).all()
        parent = list()
        for rel in rels:
            parent.append(rel.parent)
        return parent

    def is_ancestor(self, node):
        if not isinstance(node, Group) and not isinstance(node, User):
            raise TypeError("Checking object must be Group or User instance")
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
                layer_.extend(node_.parents())
            layer = layer_
        return False

    @classmethod
    def add_name_proxy(cls, fn):
        cls._name_proxy.append(fn)

    @classmethod
    def add_screen_name_proxy(cls, fn):
        cls._screen_name_proxy.append(fn)

    @classmethod
    def add_icon_proxy(cls, fn):
        cls._icon_proxy.append(fn)


class User(Node, db.Model):
    """ユーザーのモデルクラスです

    :param _id: 固有のID
    :param screen_name: ログイン名
    :param name: 名前
    :param password: パスワード
    :param icon: アイコン
    """

    __tablename__ = "mitama_user"
    password = Column(String(255))

    def to_dict(self, only_profile=False):
        profile = super().to_dict()
        if not only_profile:
            profile["parents"] = [p.to_dict(True) for p in self.parents()]
        return profile

    def load_noimage(self):
        return load_noimage_user()

    def delete(self):
        """ユーザーを削除します"""
        hook_registry.delete_user(self)
        super().delete()

    def update(self):
        """ユーザー情報を更新します"""
        super().update()
        hook_registry.update_user(self)

    def create(self):
        """ユーザーを作成します"""
        super().create()
        hook_registry.create_user(self)

    @classmethod
    def password_auth(cls, screen_name, password):
        """ログイン名とパスワードで認証します

        :param screen_name: ログイン名
        :param password: パスワード
        :return: Userインスタンス
        """
        try:
            user = cls.retrieve(screen_name=screen_name)
            if user is None:
                raise AuthorizationError("user not found")
        except:
            raise AuthorizationError("user not found")
        password = base64.b64encode(hashlib.sha256(password.encode() * 10).digest())
        if bcrypt.checkpw(password, user.password):
            return user
        else:
            raise AuthorizationError("Wrong password")

    def valid_password(self, password):
        """パスワードが安全か検証します

        :param password: パスワードのプレーンテキスト
        :return: 検証済みパスワード
        """
        config = get_from_project_dir()
        MIN_PASSWORD_LEN = config.password_validation.get('MIN_PASSWORD_LEN', None)
        COMPLICATED_PASSWORD = config.password_validation.get('COMPLICATED_PASSWORD', False)

        if MIN_PASSWORD_LEN and len(password) < MIN_PASSWORD_LEN:
            raise ValueError('パスワードは{}文字以上である必要があります'.format(MIN_PASSWORD_LEN))

        if COMPLICATED_PASSWORD and (not any(c.isdigit() for c in password)) or (not any(c.isalpha() for c in password)):
            raise ValueError('パスワードは数字とアルファベットの両方を含む必要があります')

        return password

    def set_password(self, password):
        """パスワードをハッシュ化します

        :param password: パスワードのプレーンテキスト
        :return: パスワードハッシュ
        """
        password = self.valid_password(password)
        salt = bcrypt.gensalt()
        password = base64.b64encode(hashlib.sha256(password.encode() * 10).digest())
        self.password = bcrypt.hashpw(password, salt)

    def get_jwt(self):
        nonce = "".join([str(random.randint(0, 9)) for i in range(16)])
        result = jwt.encode({"id": self._id, "nonce": nonce}, secret, algorithm="HS256")
        return result.decode()

    @classmethod
    def check_jwt(cls, token):
        """JWTからUserインスタンスを取得します

        :param token: JWT
        :return: Userインスタンス
        """
        try:
            result = jwt.decode(token, secret, algorithm="HS256")
        except jwt.exceptions.InvalidTokenError as err:
            raise AuthorizationError("Invalid token.")
        return cls.retrieve(result["id"])


class Group(Node, db.Model):
    """グループのモデルクラスです

    :param _id: 固有のID
    :param screen_name: ドメイン名
    :param name: 名前
    :param icon: アイコン
    """

    __tablename__ = "mitama_group"

    def to_dict(self, only_profile=False):
        profile = super().to_dict()
        if not only_profile:
            profile["parents"] = [n.to_dict(True) for n in self.parents()]
            profile["children"] = [n.to_dict(True) for n in self.children()]
        return profile

    def load_noimage(self):
        return load_noimage_group()

    @classmethod
    def tree(cls):
        noparent = [
            rel.child._id
            for rel in db.session.query(Relation.child).group_by(Relation.child)
            if isinstance(rel.child, Group)
        ]
        groups = [
            group
            for group in Group.query.filter().all()
            if group._id not in noparent and isinstance(group, Group)
        ]
        return groups

    def append(self, node):
        if not isinstance(node, Group) and not isinstance(node, User):
            raise TypeError("Appending object must be Group or User instance")
        rel = Relation()
        rel.parent = self
        rel.child = node
        rel.create()

    def append_all(self, nodes):
        for node in nodes:
            if not isinstance(node, Group) and not isinstance(node, User):
                raise TypeError("Appending object must be Group or User instance")
            rel = Relation()
            rel.parent = self
            rel.child = node
            Relation.query.session.add(rel)
        Relation.query.session.commit()

    def remove(self, node):
        if not isinstance(node, Group) and not isinstance(node, User):
            raise TypeError("Removing object must be Group or User instance")
        rel = (
            Relation.query.filter(Relation.parent == self)
            .filter(Relation.child == node)
            .first()
        )
        rel.delete()

    def remove_all(self, nodes):
        for node in nodes:
            if not isinstance(node, Group) and not isinstance(node, User):
                raise TypeError("Appending object must be Group or User instance")
        rels = (
            Relation.query.filter(Relation.parent == self)
            .filter(Relation.child in nodes)
            .all()
        )
        Relation.query.session.delete(rels)
        Relation.query.session.commit()

    def children(self):
        rels = Relation.query.filter(Relation.parent == self).all()
        children = list()
        for rel in rels:
            children.append(rel.child)
        return children

    def is_descendant(self, node):
        if node.__class__.__name__ != "Group" and node.__class__.__name__ != "User":
            raise TypeError("Checking object must be Group or User instance")
        layer = self.children()
        while len(layer) > 0:
            if node in layer:
                return True
            layer_ = list()
            for node_ in layer:
                if node_.__class__.__name__ == "Group":
                    layer_.extend(node_.children())
            layer = layer_
        return False

    def is_in(self, node):
        if not isinstance(node, Group) and not isinstance(node, User):
            raise TypeError("Checking object must be Group or User instance")
        rels = (
            Relation.query.filter(Relation.parent == self)
            .filter(Relation.child == node)
            .all()
        )
        return len(rels) != 0

    def delete(self):
        """グループを削除します"""
        hook_registry.delete_group(self)
        super().delete()

    def update(self):
        """グループの情報を更新します"""
        super().update()
        hook_registry.update_group(self)

    def create(self):
        """グループを作成します"""
        super().create()
        hook_registry.create_group(self)


class PermissionMixin(object):
    """パーミッションのモデルの実装を支援します

    ホワイトリスト方式の許可システムを実装する上で役に立つ機能をまとめたクラスです。
    このクラスとBaseDatabase.Modelを継承したクラスを定義するとパーミッションシステムを実現できます。

    .. code-block:: python

        class SomePermission(PermissionMixin, db.Model):
            pass

    継承先のクラスで :samp:`target` プロパティを定義した場合、特定のものに対してのみ許可する仕様にすることができます。

    .. code-block:: python

        class SomePermission(PermissionMixin, db.Model):
            target = Column(User)

    targetがUser、またはGroupの場合、targetUpPropagate、 targetDownPropagateを指定すれば、targetに対しても伝播をチェックすることができます。

    :param _id: 固有のID
    :param node: 許可するUser、またはGroupのインスタンス
    :param targetUpPropagate: targetがUser、またはGroupの場合の上向き伝播
    :param targetDownPropagate: targetがUser、またはGroupの場合の下向き伝播
    :param upPropagate: 許可対象のUser、またはGroupの場合の上向き伝播
    :param downPropagate: 許可対象のUser、またはGroupの場合の下向き伝播
    """

    @declared_attr
    def __tablename__(cls):
        return "__" + cls.__name__.lower() + "_permission"

    @declared_attr
    def __table_args__(cls):
        if hasattr(cls, "target"):
            unique = UniqueConstraint("node", "target", name="unique")
        else:
            unique = UniqueConstraint("node", name="unique")
        return (unique,)

    node = Column(NodeType)
    targetUpPropagate = False
    targetDownPropagate = False
    upPropagate = False
    downPropagate = False

    @classmethod
    def accept(cls, node, target=None):
        """UserまたはGroupに許可します

        :param node: UserまたはGroupのインスタンス
        :param target: 許可対象
        """
        perm = cls()
        perm.node = node
        if hasattr(cls, "target") and target != None:
            perm.target = target
        perm.create()

    @classmethod
    def forbit(cls, node, target=None):
        """UserまたはGroupの許可を取りやめます

        :param node: UserまたはGroupのインスタンス
        :param target: 許可対象
        """
        if hasattr(cls, "target"):
            perm = (
                cls.query.filter(cls.node == node).filter(cls.target == target).first()
            )
        else:
            perm = cls.query.filter(cls.node == node).first()
        if perm != None:
            perm.delete()

    @classmethod
    def is_accepted(cls, node, target=None):
        """UserまたはGroupが許可されているか確認します

        :param node: UserまたはGroupのインスタンス
        :param target: 許可対象
        """
        perms = cls.query.filter(cls.node == node).all()
        for perm in perms:
            if perm.is_target(target) or perm.is_target(None):
                return True
        if isinstance(node, User):
            parents = node.parents()
            for group in parents:
                if cls.is_accepted(group, target):
                    return True
        for node_ in cls.query.all():
            if node_.node == None:
                continue
            if (
                node_.upPropagate
                and not isinstance(node_.node, User)
                and node_.node.is_ancestor(node)
                and node_.is_target(target)
            ):
                return True
            if (
                node_.downPropagate
                and not isinstance(node_.node, User)
                and node_.node.is_descendant(node)
                and node_.is_target(target)
            ):
                return True
        return False

    def is_target(self, target=None):
        if not hasattr(self, "target"):
            return True
        if self.target == None:
            return True
        if self.target == target:
            return True
        if isinstance(self.target, Group):
            if isinstance(target, User):
                if self.targetUpPropagate:
                    return self.target.is_in(target) or self.target.is_ancestor(target)
                elif self.targetDownPropagate:
                    return self.target.is_descendant(target)
                else:
                    return self.target == target
            elif isinstance(target, Group):
                if self.targetUpPropagate:
                    return self.target.is_ancestor(target)
                elif self.targetDownPropagate:
                    return self.target.is_descendant(target)
                else:
                    return self.target == target
            elif self.target == target:
                return True
        return False

    @classmethod
    def is_forbidden(cls, node, target=None):
        """UserまたはGroupが許可されていないか確認します

        :param node: UserまたはGroupのインスタンス
        :param target: 許可対象
        """
        if not hasattr(cls, "target"):
            return not cls.is_accepted(node)
        else:
            return not cls.is_accepted(node, target)


db.create_all()
