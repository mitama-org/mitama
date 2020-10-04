#!/usr/bin/python
'''ベースモデル

    * アプリサイドから触るときに継承させるベースクラス
    * Djangoのdjango.db.modelsみたいなイメージ
    * データベースはユーザー管理をしているものとは別にしたいので、そのつもりで
    * UserとGroupみたいなカスタム型を使えるようになってると良い
    * Flaskのsqlalchemy拡張が参考に成る
'''

from sqlalchemy.orm import class_mapper
from sqlalchemy.ext.declarative import declarative_base, declared_attr
from sqlalchemy.types import TypeDecorator
from mitama.db.types import Column, Integer, String, Node, Group, LargeBinary
from mitama._extra import _classproperty
import re

class Model():
    _id = Column(Integer, primary_key = True)
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
        return re.sub("(.[A-Z])",lambda x:x.group(1)[0] + "_" +x.group(1)[1], cls.__name__).lower()
    def create(self):
        self.query.session.add(self)
        self.query.session.commit()
    def update(self):
        self.query.session.commit()
    def delete(self):
        self.query.session.delete(self)
        self.query.session.commit()
    @classmethod
    def list(cls, cond = None):
        if cond != None:
            return cls.query.filter(cond).all()
        else:
            return cls.query.filter().all()
    @classmethod
    def retrieve(cls, id = None):
        if id != None:
            node = cls.query.filter(cls._id == id).one()
        else:
            raise Exception('Id not given')
        return node
