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
import re

class Model:
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
