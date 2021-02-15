import unittest
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.schema import Column
from sqlalchemy.types import Integer, String
from sqlalchemy import *
from sqlalchemy.orm import mapper, sessionmaker
from sqlalchemy.engine.reflection import Inspector
import sqlite3

class TestSqlite3(unittest.TestCase):
    def test_sqlite3(self):
        testa = sqlite3.connect('testa.sqlite3')
        testb = sqlite3.connect('testb.sqlite3')
        cur = testa.cursor()
        cur.execute("pragma database_list;")
        print(cur.fetchall())
    """
    def test_attach(self):
        engine = create_engine("sqlite:///testa.sqlite3", echo=True)
        engine.execute("ATTACH DATABASE \"./testb.sqlite3\" AS test;")

        inspector = Inspector.from_engine(engine)
        print(inspector.get_table_names(schema="test"))

        metadata = MetaData(engine)
        Base = declarative_base(metadata)

        class ModelA(object):
            pass

        class ModelB(object):
            pass

        modela = Table(
            "modela",
            metadata,
            Column("id", Integer, autoincrement=True, primary_key=True),
            Column("name", String),
            schema="main",
            autoload = True,
        )
        modelb = Table(
            "modelb",
            metadata,
            Column("id", Integer, autoincrement=True, primary_key=True),
            Column("name", String),
            schema="test",
            autoload = True,
        )
        mapper(ModelA, modela)
        mapper(ModelB, modelb)
        Base.metadata.create_all(engine)

        Session = sessionmaker(bind=engine)
        session = Session()
        a = ModelA()
        a.name = "hhh"
        b = ModelB()
        b.name = "ddd"
        session.add(a)
        session.add(b)
        session.commit()
    """
