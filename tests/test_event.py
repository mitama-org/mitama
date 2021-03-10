import unittest

from mitama.db import DatabaseManager, BaseDatabase
from mitama.db.types import Column, String

DatabaseManager.test()


class Database(BaseDatabase):
    pass


db = Database()


class ModelC(db.Model):
    name = Column(String)


def addhoge(modelc):
    modelc.name = "huga"
    modelc.update()


ModelC.listen("hoge")
ModelC.event["hoge"] += addhoge


db.create_all()


class TestEvent(unittest.TestCase):
    def test_event(self):
        DatabaseManager.start_session()
        hoge = ModelC()
        hoge.name = "hoge"
        hoge.create()
        hoge.event["hoge"]()
        self.assertEqual(hoge.name, "huga")
        DatabaseManager.close_session()
        pass
