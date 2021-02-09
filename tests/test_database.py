import unittest

from mitama.db import BaseDatabase
from mitama.db.types import Column, Integer, String

db = BaseDatabase.test()


class ModelA(db.Model):
    name = Column(String)


class ModelB(db.Model):
    age = Column(Integer)


db.create_all()


class TestBaseDatabase(unittest.TestCase):
    def test_create_db(self):
        self.assertTrue(db.engine.dialect.has_table(db.engine, "model_a"))
        self.assertTrue(db.engine.dialect.has_table(db.engine, "model_b"))

    def test_insert(self):
        a = ModelA()
        a.name = "hello"
        a.create()
        self.assertEqual(ModelA.query.filter(ModelA.name == "hello").one(), a)

    def test_update(self):
        a = ModelA.query.filter(ModelA.name == "hello").one()
        a.name = "world"
        id = a._id
        a.update()
        self.assertEqual(ModelA.retrieve(id).name, "world")

    def test_retrieve(self):
        a = ModelA()
        a.name = "hogehoge"
        a.create()
        a_1 = ModelA.retrieve(a._id)
        a_2 = ModelA.retrieve(name = "hogehoge")
        self.assertEqual(a_1, a_2)

    def test_to_dict(self):
        a = ModelA.query.first()
        self.assertEqual(
            a.to_dict(),
            {
                "_id": a._id,
                "name": a.name,
            },
        )
