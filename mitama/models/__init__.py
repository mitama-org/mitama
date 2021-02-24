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
import smtplib

import bcrypt
import jwt
import magic
from sqlalchemy.ext.declarative import declarative_base, declared_attr
from sqlalchemy.schema import UniqueConstraint
from sqlalchemy import event

from mitama.db import BaseDatabase, func, ForeignKey, relationship, Table, backref
from mitama.db.types import Column, Group, Integer, LargeBinary
from mitama.db.types import Node as NodeType
from mitama.db.types import String
from mitama.db.model import UUID
from mitama.noimage import load_noimage_group, load_noimage_user
from mitama.conf import get_from_project_dir
from mitama._extra import _classproperty

class Database(BaseDatabase):
    pass

db = Database(prefix='mitama')

secret = secrets.token_hex(32)


class AuthorizationError(Exception):
    INVALID_TOKEN = 0
    WRONG_PASSWORD = 1
    USER_NOT_FOUND= 2
    def __init__(self, code):
        self.code = code
    @property
    def message(self):
        return [
            "トークンが不正です",
            "パスワードが間違っています",
            "ユーザーが見つかりません"
        ][self.code]
    pass


user_group = Table(
    "mitama_user_group",
    db.metadata,
    Column("_id", String(64), default=UUID(), primary_key=True),
    Column("group_id", String(64), ForeignKey("mitama_group._id", ondelete="CASCADE")),
    Column("user_id", String(64), ForeignKey("mitama_user._id", ondelete="CASCADE")),
)

class UserGroup(db.Model):
    __table__ = user_group
    _id = user_group.c._id
    group_id= user_group.c.group_id
    user_id = user_group.c.user_id
    user = relationship("User")
    group = relationship("Group")

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

    def icon_to_dataurl(self):
        f = magic.Magic(mime=True, uncompress=True)
        mime = f.from_buffer(self.icon)
        return "data:" + mime + ";base64," + base64.b64encode(self.icon).decode()

    @classmethod
    def add_name_proxy(cls, fn):
        cls._name_proxy.append(fn)

    @classmethod
    def add_screen_name_proxy(cls, fn):
        cls._screen_name_proxy.append(fn)

    @classmethod
    def add_icon_proxy(cls, fn):
        cls._icon_proxy.append(fn)

    @classmethod
    def retrieve(cls, _id=None, screen_name=None, **kwargs):
        if _id is not None:
            return super().retrieve(_id = _id)
        elif screen_name is not None:
            return super().retrieve(_screen_name = screen_name)
        else:
            return super().retrieve(**kwargs)

    def __eq__(self, other):
        return self._id == other._id

class User(Node, db.Model):
    """ユーザーのモデルクラスです

    :param _id: 固有のID
    :param screen_name: ログイン名
    :param name: 名前
    :param password: パスワード
    :param icon: アイコン
    """

    __tablename__ = "mitama_user"
    _id = Column(String(64), default=UUID("user"), primary_key = True, nullable=False)
    _project = None
    _token = Column(String(64))
    email = Column(String(64), nullable=False)
    password = Column(String(255))
    groups = relationship(
        "Group",
        secondary=user_group,
    )

    def to_dict(self, only_profile=False):
        profile = super().to_dict()
        if not only_profile:
            profile["groups"] = [p.to_dict(True) for p in self.groups()]
        return profile

    def load_noimage(self):
        return load_noimage_user()

    def delete(self):
        """ユーザーを削除します"""
        from mitama.app.hook import HookRegistry
        hook_registry = HookRegistry()
        hook_registry.delete_user(self)
        super().delete()

    def update(self):
        """ユーザー情報を更新します"""
        super().update()
        from mitama.app.hook import HookRegistry
        hook_registry = HookRegistry()
        hook_registry.update_user(self)

    def create(self):
        """ユーザーを作成します"""
        super().create()
        from mitama.app.hook import HookRegistry
        hook_registry = HookRegistry()
        hook_registry.create_user(self)

    def password_check(self, password):
        password = base64.b64encode(hashlib.sha256(password.encode() * 10).digest())
        password_ = self.password
        if isinstance(password_, str):
            password_ = password_.encode()
        return bcrypt.checkpw(password, password_)

    @classmethod
    def password_auth(cls, screen_name, password):
        """ログイン名とパスワードで認証します

        :param screen_name: ログイン名
        :param password: パスワード
        :return: Userインスタンス
        """
        try:
            user = cls.retrieve(_screen_name=screen_name)
            if user is None:
                raise AuthorizationError(AuthorizationError.USER_NOT_FOUND)
        except:
            raise AuthorizationError(AuthorizationError.USER_NOT_FOUND)
        password = base64.b64encode(hashlib.sha256(password.encode() * 10).digest())
        password_ = user.password
        if isinstance(password_, str):
            password_ = password_.encode()
        if bcrypt.checkpw(password, password_):
            return user
        else:
            raise AuthorizationError(AuthorizationError.WRONG_PASSWORD)

    def valid_password(self, password):
        """パスワードが安全か検証します

        :param password: パスワードのプレーンテキスト
        :return: 検証済みパスワード
        """
        if self._project is None:
            return password
        project = self._project
        if project.password_validation is None:
            return password
        MIN_PASSWORD_LEN = project.password_validation.get('min_password_len', None)
        COMPLICATED_PASSWORD = project.password_validation.get('complicated_password', False)

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

    def mail(self, subject, body, type="html"):
        self._project.send_mail(self.email, subject, body, type)

    def get_jwt(self):
        nonce = "".join([str(random.randint(0, 9)) for i in range(16)])
        result = jwt.encode({"id": self._id, "nonce": nonce}, secret, algorithm="HS256")
        #return result.decode()
        return result

    @classmethod
    def check_jwt(cls, token):
        """JWTからUserインスタンスを取得します

        :param token: JWT
        :return: Userインスタンス
        """
        try:
            result = jwt.decode(token, secret, algorithms="HS256")
        except jwt.exceptions.InvalidTokenError as err:
            raise AuthorizationError(AuthorizationError.INVALID_TOKEN)
        return cls.retrieve(result["id"])

    def is_ancestor(self, node):
        if not isinstance(node, Group) and not isinstance(node, User):
            raise TypeError("Checking object must be Group or User instance")
        layer = self.groups
        while len(layer) > 0:
            if isinstance(node, Group) and node in layer:
                return True
            else:
                for node_ in layer:
                    if isinstance(node, User) and node_.is_in(node):
                        return True
            layer_ = list()
            for node_ in layer:
                layer_.extend(node_.groups)
            layer = layer_
        return False


class Group(Node, db.Model):
    """グループのモデルクラスです

    :param _id: 固有のID
    :param screen_name: ドメイン名
    :param name: 名前
    :param icon: アイコン
    """

    __tablename__ = "mitama_group"
    _id = Column(String(64), default=UUID("group"), primary_key=True, nullable=False)
    _project = None
    users = relationship(
        "User",
        secondary=user_group,
    )
    parent_id = Column(String(64), ForeignKey("mitama_group._id"))
    groups = relationship(
        "Group",
        backref=backref("parent", remote_side=[_id]),
    )

    def to_dict(self, only_profile=False):
        profile = super().to_dict()
        if not only_profile:
            profile["parent"] = self.parent.to_dict()
            profile["groups"] = [n.to_dict(True) for n in self.groups ]
            profile["users"] = [n.to_dict(True) for n in self.users ]
        return profile

    def load_noimage(self):
        return load_noimage_group()

    @_classproperty
    def relation(cls):
        return Column(String, ForeignKey("mitama_group._id"), nullable=False)

    @_classproperty
    def relations(cls):
        return relation("mitama_group._id", cascade="all, delete")

    @_classproperty
    def relation_or_null(cls):
        return Column(String, ForeignKey("mitama_group._id"), nullable=True)

    @classmethod
    def tree(cls):
        return Group.query.filter(Group.parent == None).all()

    def append(self, node):
        if isinstance(node, User):
            self.users.append(node)
        elif isinstance(node, Group):
            self.groups.append(node)
        else:
            raise TypeError("Appending object must be Group or User instance")
        self.query.session.commit()

    def append_all(self, nodes):
        for node in nodes:
            if isinstance(node, User):
                self.users.append(node)
            elif isinstance(node, Group):
                self.groups.append(node)
            else:
                raise TypeError("Appending object must be Group or User instance")
        self.query.session.commit()

    def remove(self, node):
        if not isinstance(node, Group) and not isinstance(node, User):
            raise TypeError("Removing object must be Group or User instance")
        if isinstance(node, Group):
            self.groups.remove(node)
        else:
            self.users.remove(node)
        self.query.session.commit()

    def remove_all(self, nodes):
        for node in nodes:
            if not isinstance(node, Group) and not isinstance(node, User):
                raise TypeError("Appending object must be Group or User instance")
            if isinstance(node, Group):
                self.groups.remove(node)
            else:
                self.users.remove(node)
        self.query.session.commit()

    def is_ancestor(self, node):
        if not isinstance(node, Group) and not isinstance(node, User):
            raise TypeError("Checking object must be Group or User instance")
        if self.parent is None:
            return False
        layer = [self.parent]
        while len(layer) > 0:
            if isinstance(node, Group) and node in layer:
                return True
            else:
                for node_ in layer:
                    if isinstance(node, User) and node_.is_in(node):
                        return True
            layer_ = list()
            for node_ in layer:
                layer_.extend([node_.parent])
            layer = layer_
        return False

    def is_descendant(self, node):
        if not isinstance(node, Group) and not isinstance(node, User):
            raise TypeError("Checking object must be Group or User instance")
        layer = self.groups
        while len(layer) > 0:
            if node in layer:
                return True
            layer_ = list()
            for node_ in layer:
                layer_.extend(node_.groups)
            layer = layer_
        return False

    def is_in(self, node):
        if isinstance(node, User):
            return node in self.users
        elif isinstance(node, Group):
            return node in self.groups
        else:
            raise TypeError("Checking object must be Group or User instance")

    def delete(self):
        """グループを削除します"""
        from mitama.app.hook import HookRegistry
        hook_registry = HookRegistry()
        hook_registry.delete_group(self)
        super().delete()

    def update(self):
        """グループの情報を更新します"""
        super().update()
        from mitama.app.hook import HookRegistry
        hook_registry = HookRegistry()
        hook_registry.update_group(self)

    def create(self):
        """グループを作成します"""
        super().create()
        from mitama.app.hook import HookRegistry
        hook_registry = HookRegistry()
        hook_registry.create_group(self)

    def mail(self, subject, body, type="html", to_all=False):
        for user in self.users:
            user.mail(subject, body, type)
        if to_all:
            for group in self.groups:
                group.mail(subject, body, type, to_all)


role_user = Table(
    "mitama_role_user",
    db.metadata,
    Column("role_id", String(64), ForeignKey("mitama_role._id", ondelete="CASCADE")),
    Column("user_id", String(64), ForeignKey("mitama_user._id", ondelete="CASCADE"))
)

role_group = Table(
    "mitama_role_group",
    db.metadata,
    Column("role_id", String(64), ForeignKey("mitama_role._id", ondelete="CASCADE")),
    Column("group_id", String(64), ForeignKey("mitama_group._id", ondelete="CASCADE"))
)


class Role(db.Model):
    __tablename__ = "mitama_role"
    screen_name = Column(String(64), unique=True, nullable=False)
    name = Column(String(64))
    users = relationship(
        "User",
        secondary=role_user,
        backref="roles",
        cascade="all, delete"
    )
    groups = relationship(
        "Group",
        secondary=role_group,
        backref="roles",
        cascade="all, delete"
    )

    def append(self, node):
        if isinstance(node, Group):
            self.groups.append(node)
        else:
            self.users.append(node)
        self.update()

    def remove(self, node):
        if isinstance(node, Group):
            self.groups.remove(node)
        else:
            self.users.remove(node)
        self.update()


role_relation = Table(
    "mitama_role_relation",
    db.metadata,
    Column("_id", String(64), default=UUID(), primary_key=True),
    Column("role_id", String(64), ForeignKey("mitama_inner_role._id", ondelete="CASCADE")),
    Column("relation_id", String(64), ForeignKey("mitama_user_group._id", ondelete="CASCADE"))
)

class RoleRelation(db.Model):
    __table__ = role_relation
    _id = role_relation.c._id
    role_id = role_relation.c.role_id
    relation_id = role_relation.c.relation_id

class InnerRole(db.Model):
    __tablename__ = "mitama_inner_role"
    screen_name = Column(String(64), unique=True, nullable=False)
    name = Column(String(64))
    relations = relationship(
        "UserGroup",
        secondary=role_relation,
        backref="roles",
        cascade="all, delete"
    )

    def append(self, group, user):
        relation = UserGroup.retrieve(group=group, user=user)
        self.relations.append(relation)
        self.update()

    def remove(self, group, user):
        relation = UserGroup.retrieve(group=group, user=user)
        self.relations.remove(relation)
        self.update()

    def exists(self, group, user):
        relation = UserGroup.retrieve(group=group, user=user)
        return relation in self.relations

def permission(db_, permissions):
    role_permission = Table(
        db_.Model.prefix + "_role_permission",
        db_.metadata,
        Column("role_id", String(64), ForeignKey("mitama_role._id", ondelete="CASCADE"), primary_key=True),
        Column("permission_id", String(64), ForeignKey(db.Model.prefix + "_permission._id", ondelete="CASCADE"), primary_key=True),
        extend_existing=True
    )

    class Permission(db_.Model):
        name = Column(String(64))
        screen_name = Column(String(64), unique = True)
        roles = relationship(
            "Role",
            secondary=role_permission,
            backref="permissions",
            cascade="all, delete"
        )

        @classmethod
        def accept(cls, screen_name, role):
            """特定のRoleに許可します """
            permission = cls.retrieve(screen_name=screen_name)
            permission.roles.append(role)
            permission.update()

        @classmethod
        def forbit(cls, screen_name, role):
            """UserまたはGroupの許可を取りやめます """
            permission = cls.retrieve(screen_name=screen_name)
            permission.roles.remove(role)
            permission.update()

        @classmethod
        def is_accepted(cls, screen_name, node):
            """UserまたはGroupが許可されているか確認します
            """
            perm = cls.retrieve(screen_name=screen_name)
            for role in perm.roles:
                if isinstance(node, User):
                    if node in role.users:
                        return True
                    for group in role.groups:
                        if group.is_in(node):
                            return True
                else:
                    if node in role.groups:
                        return True
            return False

        @classmethod
        def is_forbidden(cls, screen_name, node):
            """UserまたはGroupが許可されていないか確認します
            """
            return not cls.is_accepted(screen_name, node)

    def after_create(target, conn, **kw):
        for perm_ in permissions:
            perm = Permission()
            perm.name = perm_["name"]
            perm.screen_name = perm_["screen_name"]
            Permission.query.session.add(perm)
        Permission.query.session.commit()

    event.listen(Permission.__table__, "after_create", after_create)

    return Permission


def inner_permission(db_, permissions):
    inner_role_permission = Table(
        db_.Model.prefix + "_inner_role_permission",
        db_.metadata,
        Column("role_id", String(64), ForeignKey("mitama_inner_role._id", ondelete="CASCADE")),
        Column("permission_id", String(64), ForeignKey(db.Model.prefix + "_inner_permission._id", ondelete="CASCADE")),
        extend_existing=True
    )

    class InnerPermission(db_.Model):
        name = Column(String(64))
        screen_name = Column(String(64), unique = True)
        roles = relationship(
            "InnerRole",
            secondary=inner_role_permission,
            backref="permissions",
            cascade="all, delete"
        )

        @classmethod
        def accept(cls, screen_name, role):
            """特定のRoleに許可します """
            permission = cls.retrieve(screen_name = screen_name)
            permission.roles.append(role)
            permission.update()

        @classmethod
        def forbit(cls, screen_name, role):
            """UserまたはGroupの許可を取りやめます """
            permission = cls.retrieve(screen_name = screen_name)
            permission.roles.remove(role)
            permission.update()

        @classmethod
        def is_accepted(cls, screen_name, group, user):
            """UserまたはGroupが許可されているか確認します
            """
            rel = UserGroup.retrieve(user=user, group=group)
            permission = cls.retrieve(screen_name = screen_name)
            for role in permission.roles:
                if rel in role.relations:
                    return True
            return False

        @classmethod
        def is_forbidden(cls, screen_name, group, node):
            """UserまたはGroupが許可されていないか確認します
            """
            return not cls.is_accepted(screen_name, node)

    def after_create(target, conn, **kw):
        for perm_ in permissions:
            perm = InnerPermission()
            perm.name = perm_["name"]
            perm.screen_name = perm_["screen_name"]
            InnerPermission.query.session.add(perm)
        InnerPermission.query.session.commit()

    event.listen(InnerPermission.__table__, "after_create", after_create)

    return InnerPermission

Permission = permission(db, [
    {
        "name": "権限管理",
        "screen_name": "admin"
    },
    {
        "name": "グループ作成",
        "screen_name": "create_group",
    },
    {
        "name": "グループ更新",
        "screen_name": "update_group",
    },
    {
        "name": "グループ削除",
        "screen_name": "delete_group",
    },
    {
        "name": "ユーザー作成",
        "screen_name": "create_user",
    },
    {
        "name": "ユーザー更新",
        "screen_name": "update_user",
    },
    {
        "name": "ユーザー削除",
        "screen_name": "delete_user",
    }
])

InnerPermission = inner_permission(db, [
    {
        "name": "グループ管理",
        "screen_name": "admin"
    },
    {
        "name": "ユーザー追加",
        "screen_name": "add_user",
    },
    {
        "name": "ユーザー削除",
        "screen_name": "remove_user"
    },
    {
        "name": "グループ追加",
        "screen_name": "add_group"
    },
    {
        "name": "グループ削除",
        "screen_name": "remove_group"
    }
])

db.create_all()
