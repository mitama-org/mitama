#!/usr/bin/python
"""データベース

データベースの接続とか抽象化の処理を書きます
Databaseはシングルトンの接続のインスタンスを生成するクラスです
各アプリにはDatabaseを継承したクラスを定義してもらい、そいつのModelプロパティのベースクラスからモデルを作ってもらいます。
"""

import inspect as _inspect

from sqlalchemy import *
from sqlalchemy.engine import *
from sqlalchemy.schema import *
from sqlalchemy.inspection import inspect
from sqlalchemy.sql import *
from sqlalchemy.types import *
from sqlalchemy.orm import *
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.declarative.api import DeclarativeMeta
from sqlalchemy.orm.exc import UnmappedClassError
from sqlalchemy.sql import func

from mitama._extra import _Singleton

from .driver.sqlite3 import get_test_engine
from .model import Model


class _QueryProperty:
    def __init__(self, db):
        self.db = db

    def __get__(self, obj, type):
        try:
            mapper = class_mapper(type)
            if mapper:
                return Query([type]).with_session(self.db.session)
        except UnmappedClassError:
            return None


class DatabaseManager(_Singleton):
    engine = None
    metadata = None
    session = None

    @classmethod
    def test(cls):
        cls.set_engine(get_test_engine())

    @classmethod
    def set_engine(cls, engine):
        cls.engine = engine
        cls.metadata = MetaData(cls.engine)
        cls.session = Session(autocommit=False, autoflush=False, bind=engine)
        cls.Model = declarative_base(cls=Model, name="Model", metadata=cls.metadata)

    def __init__(self, database=None):
        if database is not None:
            if database["type"] == "mysql":
                engine = create_engine(
                    "mysql://{}:{}@{}/{}?charset=utf8mb4".format(
                        database["user"],
                        database["password"],
                        database["host"],
                        database["name"]
                    )
                )
            elif database["type"] == "postgresql":
                engine = create_engine(
                    "postgresql://{}:{}@{}/{}?charset=utf8".format(
                        database["user"],
                        database["password"],
                        database["host"],
                        database["name"]
                    ),
                    echo=True
                )
            else:
                engine = create_engine("sqlite:///" + str(database["path"]))
            self.set_engine(engine)


class _Database():
    def __init__(self, model=None, metadata=None, query_class=Query):
        self.manager = DatabaseManager()
        self.Query = query_class
        self.Model = self.make_declarative_base(model, metadata)

    def make_declarative_base(self, model=None, metadata=None):
        if model == None:
            model = self.manager.Model
        if not isinstance(model, DeclarativeMeta):
            model = declarative_base(cls=model, name="Model", metadata=metadata)
        if metadata is not None and model.metadata is not metadata:
            model.metadata = metadata
        else:
            model.metadata = self.metadata
        if not getattr(model, "query_class", None):
            model.query_class = self.Query
        model.query = _QueryProperty(self)
        return model

    @property
    def engine(self):
        return self.manager.engine

    @property
    def metadata(self):
        return self.manager.metadata

    @property
    def session(self):
        return self.manager.session

    def create_all(self):
        self.metadata.create_all(self.engine)


class BaseDatabase(_Database):
    """アプリで利用するデータベースの操作を行うクラス

    アプリからデータベースを使うたい場合、このクラスを継承したクラスをアプリ内に定義します。
    """

    def __init__(self, prefix=None, model=None, metadata=None, query_class=Query):
        super().__init__(
            model = model,
            metadata = metadata,
            query_class = query_class
        )
        if prefix == None:
            prefix = _inspect.getmodule(self.__class__).__package__
        self.Model.prefix = prefix
