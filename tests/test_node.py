import unittest

from mitama.db import _CoreDatabase, BaseDatabase

db = _CoreDatabase.test()

from mitama.models import Group, User
from mitama.db.types import Column, Node

db_ = BaseDatabase.test()

class ModelC(db_.Model):
    node = Column(Node)

db_.create_all()

class TestNode(unittest.TestCase):
    def test_node(self):
        group = Group()
        group.name = "team1"
        group.screen_name = "team1"
        user1 = User()
        user1.name = "bob"
        user1.screen_name = "bob"
        group.create()
        user1.create()
        hoge = ModelC()
        hoge.node = group
        hoge.create()
        piyo = ModelC()
        piyo.node = user1
        piyo.create()
        foo = ModelC()
        foo.node = group._id
        foo.create()
        bar= ModelC()
        bar.node = user1._id
        bar.create()
        self.assertEqual(hoge.node, group)
        self.assertEqual(piyo.node, user1)
        self.assertEqual(foo.node, group)
        self.assertEqual(bar.node, user1)
        pass
