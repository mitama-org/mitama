#!/usr/bin/python
'''ベースモデル

    * アプリサイドから触るときに継承させるベースクラス
    * Djangoのdjango.db.modelsみたいなイメージ
    * データベースはユーザー管理をしているものとは別にしたいので、そのつもりで
    * UserとGroupみたいなカスタム型を使えるようになってると良い
    * Flaskのsqlalchemy拡張が参考に成る
'''

from sqlalchemy.orm import class_mapper
from sqlalchemy.ext.declarative import declarative_base

class Model:
    def create(self):
        self.query.session.add(self)
        self.query.session.commit()
    def update(self):
        self.query.session.commit()
    def delete(self):
        self.query.session.delete(self)
        self.query.session.commit()
