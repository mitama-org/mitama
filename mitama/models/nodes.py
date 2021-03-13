import base64
import hashlib
import random
import secrets
from pywebpush import webpush

import bcrypt
import jwt
import magic
import json
from Crypto.Random import get_random_bytes
from Crypto.Hash import SHA256

from mitama.db import ForeignKey, relationship, Table, backref
from mitama.db.types import Column, LargeBinary
from mitama.db.types import String
from mitama.db.model import UUID
from mitama.noimage import load_noimage_group, load_noimage_user
from mitama._extra import _classproperty

from .core_db import db

secret = secrets.token_hex(32)


class AuthorizationError(Exception):
    INVALID_TOKEN = 0
    WRONG_PASSWORD = 1
    USER_NOT_FOUND = 2

    def __init__(self, code):
        self.code = code

    @property
    def message(self):
        return [
            "トークンが不正です",
            "パスワードが間違っています",
            "ユーザーが見つかりません"
        ][self.code]

    def __str__(self):
        return self.message


user_group = Table(
    "mitama_user_group",
    db.metadata,
    Column("_id", String(64), default=UUID(), primary_key=True),
    Column(
        "group_id",
        String(64),
        ForeignKey("mitama_group._id", ondelete="CASCADE")
    ),
    Column(
        "user_id",
        String(64),
        ForeignKey("mitama_user._id", ondelete="CASCADE")
    ),
)


class UserGroup(db.Model):
    __table__ = user_group
    _id = user_group.c._id
    group_id = user_group.c.group_id
    user_id = user_group.c.user_id
    user = relationship("User")
    group = relationship("Group")


class AbstractNode(object):
    _icon = Column(LargeBinary)
    _name = Column("name", String(255))
    _screen_name = Column("screen_name", String(255))
    _name_proxy = list()
    _screen_name_proxy = list()
    _icon_proxy = list()

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
        if self._icon is not None:
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
        return "".join([
            "data:",
            mime,
            ";base64,",
            base64.b64encode(self.icon).decode()
        ])

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
            return super().retrieve(_id=_id)
        elif screen_name is not None:
            return super().retrieve(_screen_name=screen_name)
        else:
            return super().retrieve(**kwargs)

    def __eq__(self, other):
        return self._id == other._id


class User(AbstractNode, db.Model):
    """ユーザーのモデルクラスです

    :param _id: 固有のID
    :param screen_name: ログイン名
    :param name: 名前
    :param password: パスワード
    :param icon: アイコン
    """

    __tablename__ = "mitama_user"
    _id = Column(
        String(64),
        default=UUID("user"),
        primary_key=True,
        nullable=False
    )
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

    def password_check(self, password):
        password = base64.b64encode(
            hashlib.sha256(password.encode() * 10).digest()
        )
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
        except Exception:
            raise AuthorizationError(AuthorizationError.USER_NOT_FOUND)
        password = base64.b64encode(
            hashlib.sha256(password.encode() * 10).digest()
        )
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
        MIN_PASSWORD_LEN = project.password_validation.get(
            'min_password_len',
            None
        )
        COMPLICATED_PASSWORD = project.password_validation.get(
            'complicated_password',
            False
        )

        if MIN_PASSWORD_LEN and len(password) < MIN_PASSWORD_LEN:
            raise ValueError('パスワードは{}文字以上である必要があります'.format(MIN_PASSWORD_LEN))

        if (
            COMPLICATED_PASSWORD and (
                not any(c.isdigit() for c in password)
            ) or (not any(c.isalpha() for c in password))
        ):
            raise ValueError('パスワードは数字とアルファベットの両方を含む必要があります')

        return password

    def set_password(self, password):
        """パスワードをハッシュ化します

        :param password: パスワードのプレーンテキスト
        :return: パスワードハッシュ
        """
        password = self.valid_password(password)
        salt = bcrypt.gensalt()
        password = base64.b64encode(
            hashlib.sha256(password.encode() * 10).digest()
        )
        self.password = bcrypt.hashpw(password, salt)

    def mail(self, subject, body, type="html"):
        self._project.send_mail(self.email, subject, body, type)

    def get_jwt(self):
        nonce = "".join([str(random.randint(0, 9)) for i in range(16)])
        result = jwt.encode({
            "id": self._id,
            "nonce": nonce
        }, secret, algorithm="HS256")
        return result

    @classmethod
    def check_jwt(cls, token):
        """JWTからUserインスタンスを取得します

        :param token: JWT
        :return: Userインスタンス
        """
        try:
            result = jwt.decode(token, secret, algorithms="HS256")
        except jwt.exceptions.InvalidTokenError:
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

    def push(self, data):
        for subscription in self.subscriptions:
            subscription.push(data)


class Group(AbstractNode, db.Model):
    """グループのモデルクラスです

    :param _id: 固有のID
    :param screen_name: ドメイン名
    :param name: 名前
    :param icon: アイコン
    """

    __tablename__ = "mitama_group"
    _id = Column(
        String(64),
        default=UUID("group"),
        primary_key=True,
        nullable=False
    )
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
            profile["groups"] = [n.to_dict(True) for n in self.groups]
            profile["users"] = [n.to_dict(True) for n in self.users]
        return profile

    def load_noimage(self):
        return load_noimage_group()

    @_classproperty
    def relation(cls):
        return Column(String, ForeignKey("mitama_group._id"), nullable=False)

    @_classproperty
    def relations(cls):
        return relationship("mitama_group._id", cascade="all, delete")

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
                raise TypeError(
                    "Appending object must be Group or User instance"
                )
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
                raise TypeError(
                    "Appending object must be Group or User instance"
                )
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
                if node_.parent is not None:
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

    def __contains__(self, node):
        return self.is_in(node)

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


def get_random_token():
    s = get_random_bytes(32)
    h = SHA256.new()
    h.update(s)
    return h.hexdigest()


class UserInvite(db.Model):
    __tablename__ = "mitama_user_invite"
    token = Column(String(64), default=get_random_token, unique=True)
    email = Column(String(255))
    screen_name = Column(String(255))
    name = Column(String(255))
    _icon = Column(LargeBinary)
    roles = Column(String(255), default="")

    def load_noimage(self):
        return load_noimage_user()

    @property
    def icon(self):
        return self._icon or self.load_noimage()

    def icon_to_dataurl(self):
        f = magic.Magic(mime=True, uncompress=True)
        mime = f.from_buffer(self.icon)
        return ''.join([
            "data:",
            mime,
            ";base64,",
            base64.b64encode(self.icon).decode()
        ])

    def mail(self, subject, body, type="html"):
        self._project.send_mail(self.email, subject, body, type)


role_user = Table(
    "mitama_role_user",
    db.metadata,
    Column(
        "role_id",
        String(64),
        ForeignKey("mitama_role._id", ondelete="CASCADE")
    ),
    Column(
        "user_id",
        String(64),
        ForeignKey("mitama_user._id", ondelete="CASCADE")
    )
)

role_group = Table(
    "mitama_role_group",
    db.metadata,
    Column(
        "role_id",
        String(64),
        ForeignKey("mitama_role._id", ondelete="CASCADE")
    ),
    Column(
        "group_id",
        String(64),
        ForeignKey("mitama_group._id", ondelete="CASCADE")
    )
)


class Role(db.Model):
    __tablename__ = "mitama_role"
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
    Column(
        "role_id",
        String(64),
        ForeignKey("mitama_inner_role._id", ondelete="CASCADE")
    ),
    Column(
        "relation_id",
        String(64),
        ForeignKey("mitama_user_group._id", ondelete="CASCADE")
    )
)


class RoleRelation(db.Model):
    __table__ = role_relation
    _id = role_relation.c._id
    role_id = role_relation.c.role_id
    relation_id = role_relation.c.relation_id


class InnerRole(db.Model):
    __tablename__ = "mitama_inner_role"
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


class Node(db.Model):
    __tablename__ = "mitama_node"
    user_id = Column(
        String(64),
        ForeignKey("mitama_user._id", ondelete="CASCADE"),
        unique=True
    )
    group_id = Column(
        String(64),
        ForeignKey("mitama_group._id", ondelete="CASCADE"),
        unique=True
    )
    user = relationship(User)
    group = relationship(Group)

    @classmethod
    def retrieve(cls, obj=None, id=None, **kwargs):
        if obj is not None:
            if isinstance(obj, str):
                if obj.split("-")[0] == "user":
                    obj = User.retrieve(obj)
                else:
                    obj = Group.retrieve(obj)
            try:
                if isinstance(obj, User):
                    return cls.query.filter(cls.user == obj).one()
                else:
                    return cls.query.filter(cls.group == obj).one()
            except Exception:
                if isinstance(obj, User):
                    node = cls()
                    node.user = obj
                    node.create()
                    return node
                else:
                    node = cls()
                    node.group = obj
                    node.create()
                    return node
        else:
            return super().retrieve(id=id, **kwargs)

    @property
    def object(self):
        return self.user if self.user is not None else self.group

    def is_ancestor(self, node):
        if self.group is not None:
            return self.group.is_ancestor(node)
        else:
            return False

    def is_descendant(self, node):
        if self.group is not None:
            return self.group.is_descendant(node)
        else:
            return False

    def is_in(self, node):
        if self.group is not None:
            return self.group.is_in(node)
        else:
            return False

    def __contains__(self, node):
        return self.is_in(node)


class PushSubscription(db.Model):
    __tablename__ = "mitama_push_subscription"
    _project = None
    user_id = Column(
        String(64),
        ForeignKey("mitama_user._id", ondelete="CASCADE")
    )
    user = relationship("User", backref="subscriptions")
    subscription = Column(String(1024))

    def push(self, data):
        try:
            webpush(
                subscription_info=json.loads(self.subscription),
                data=json.dumps(data),
                vapid_private_key=self._project.vapid['private_key'],
                vapid_claims={
                    "sub": "mailto:{}".format(self._project.vapid['mailto'])
                }
            )
        except Exception as err:
            print(err)
