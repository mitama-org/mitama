import unittest
from pprint import pprint

from mitama.db import _CoreDatabase, BaseDatabase, relationship
from mitama.db import ForeignKey

db_ = _CoreDatabase.test()
db = BaseDatabase.test()

from mitama.db.types import *
from mitama.models import Group, User

print(db_.metadata)

class Hoge(db.Model):
    group_id = Column(
        String,
        ForeignKey("{}.{}._id".format(db_.schema, Group.__tablename__)),
        primary_key=True
    )
    group = relationship(Group, foreign_keys=[Group._id])

db.create_all()


class TestForeignKey(unittest.TestCase):
    def test_group(self):
        group = Group()
        group.name = "team1"
        group.screen_name = "team1"
        group.create()
        hoge = Hoge()
        hoge.group = group
        hoge.create()

        hoge_ = Hoge.retrieve(hoge._id)
        self.assertEqual(
            hoge_.group,
            group
        )
        pass
