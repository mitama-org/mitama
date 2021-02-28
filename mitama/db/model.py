#!/usr/bin/python
"""ベースモデル

    * アプリサイドから触るときに継承させるベースクラス
    * Djangoのdjango.db.modelsみたいなイメージ
    * データベースはユーザー管理をしているものとは別にしたいので、そのつもりで
    * UserとGroupみたいなカスタム型を使えるようになってると良い
    * Flaskのsqlalchemy拡張が参考に成る
"""

import uuid

from sqlalchemy.ext.declarative import declarative_base, declared_attr
from sqlalchemy.orm import ColumnProperty, class_mapper
from sqlalchemy.types import TypeDecorator

from mitama._extra import _classproperty, tosnake

from .types import Column, Group, Integer, LargeBinary, Node, String
from .event import Event

def UUID(prefix = None):
    def genUUID():
        s = str(uuid.uuid4())
        if prefix is not None:
            s = prefix + "-" + s
        return s
    return genUUID

class Model:
    prefix = None
    _id = Column(String(64), default=UUID(), primary_key=True, nullable=False)
    _event_handlers = {
        "create": Event(),
        "update": Event(),
        "delete": Event()
    }

    @classmethod
    def attribute_names(cls):
        return [
            prop.key
            for prop in class_mapper(cls).iterate_properties
            if isinstance(prop, ColumnProperty)
        ]

    def to_dict(self):
        attrs = self.attribute_names()
        d = dict()
        for k, v in self.__dict__.items():
            if k in attrs and (k == "_id" or k[0] != "_"):
                d[k] = v
        return d

    @_classproperty
    def type(cls):
        class Type(TypeDecorator):
            impl = Integer

            def process_bind_param(self, value, dialect):
                if value == None:
                    return None
                else:
                    return value._id

            def process_result_value(self, value, dialect):
                if value == None:
                    return None
                else:
                    user = cls.retrieve(value)
                    return user

        return Type

    @declared_attr
    def __tablename__(cls):
        return ("" if cls.prefix is None else cls.prefix + "_")  + tosnake(cls.__name__)

    def create(self):
        self.query.session.add(self)
        self.query.session.commit()
        try:
            self.on("create")(self)
        except Exception:
            pass

    def update(self):
        self.query.session.commit()
        try:
            self.on("update")(self)
        except Exception:
            pass

    def delete(self):
        self.query.session.delete(self)
        self.query.session.commit()
        try:
            self.on("delete")(self)
        except Exception:
            pass

    def on(self, evt):
        return self._event_handlers[evt]

    @classmethod
    def list(cls, cond=None):
        if cond != None:
            return cls.query.filter(cond).all()
        else:
            return cls.query.filter().all()

    @classmethod
    def retrieve(cls, id=None, **kwargs):
        if id != None:
            node = cls.query.filter(cls._id == id).one()
        elif len(kwargs) > 0:
            q = cls.query
            for attr, value in kwargs.items():
                q = q.filter(getattr(cls, attr) == value)
            node = q.one()
        else:
            raise Exception("Identity not given")
        return node
