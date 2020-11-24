import unittest

from mitama.db import BaseDatabase, _CoreDatabase
from mitama.db.types import Column

_CoreDatabase.test()

from mitama.models import Group, PermissionMixin, User

groups = list()
users = list()
for i in range(5):
    group = Group()
    group.name = "g" + str(i)
    group.screen_name = "g" + str(i)
    group.create()
    user = User()
    user.name = "u" + str(i)
    user.screen_name = "u" + str(i)
    user.create()
    group.append(user)
    groups.append(group)
    users.append(user)
    if i != 0:
        groups[i - 1].append(group)


class TestPermission(unittest.TestCase):
    def test_up_propagate(self):
        db = BaseDatabase.test()

        class PermissionA(PermissionMixin, db.Model):
            upPropagate = True
            downPropagate = False

        db.create_all()
        PermissionA.accept(groups[2])
        self.assertTrue(PermissionA.is_accepted(groups[0]))
        self.assertTrue(PermissionA.is_accepted(groups[1]))
        self.assertTrue(PermissionA.is_accepted(groups[2]))
        self.assertTrue(PermissionA.is_forbidden(groups[3]))
        self.assertTrue(PermissionA.is_forbidden(groups[4]))
        self.assertTrue(PermissionA.is_accepted(users[0]))
        self.assertTrue(PermissionA.is_accepted(users[1]))
        self.assertTrue(PermissionA.is_accepted(users[2]))
        self.assertTrue(PermissionA.is_forbidden(users[3]))
        self.assertTrue(PermissionA.is_forbidden(users[4]))

    def test_down_propagate(self):
        db = BaseDatabase.test()

        class PermissionB(PermissionMixin, db.Model):
            upPropagate = False
            downPropagate = True

        db.create_all()
        PermissionB.accept(groups[2])
        self.assertTrue(PermissionB.is_forbidden(groups[0]))
        self.assertTrue(PermissionB.is_forbidden(groups[1]))
        self.assertTrue(PermissionB.is_accepted(groups[2]))
        self.assertTrue(PermissionB.is_accepted(groups[3]))
        self.assertTrue(PermissionB.is_accepted(groups[4]))
        self.assertTrue(PermissionB.is_forbidden(users[0]))
        self.assertTrue(PermissionB.is_forbidden(users[1]))
        self.assertTrue(PermissionB.is_accepted(users[2]))
        self.assertTrue(PermissionB.is_accepted(users[3]))
        self.assertTrue(PermissionB.is_accepted(users[4]))

    def test_target_up_propagate(self):
        db = BaseDatabase.test()

        class PermissionC(PermissionMixin, db.Model):
            target = Column(Group.type)
            targetUpPropagate = True
            targetDownPropagate = False

        db.create_all()
        PermissionC.accept(users[2], groups[2])
        self.assertTrue(PermissionC.is_accepted(users[2], groups[0]))
        self.assertTrue(PermissionC.is_accepted(users[2], groups[1]))
        self.assertTrue(PermissionC.is_accepted(users[2], groups[2]))
        self.assertTrue(PermissionC.is_forbidden(users[2], groups[3]))
        self.assertTrue(PermissionC.is_forbidden(users[2], groups[4]))
        self.assertTrue(PermissionC.is_accepted(users[2], users[0]))
        self.assertTrue(PermissionC.is_accepted(users[2], users[1]))
        self.assertTrue(PermissionC.is_accepted(users[2], users[2]))
        self.assertTrue(PermissionC.is_forbidden(users[2], users[3]))
        self.assertTrue(PermissionC.is_forbidden(users[2], users[4]))

    def test_target_down_propagate(self):
        db = BaseDatabase.test()

        class PermissionD(PermissionMixin, db.Model):
            target = Column(Group.type)
            targetUpPropagate = False
            targetDownPropagate = True

        db.create_all()
        PermissionD.accept(users[2], groups[2])
        self.assertTrue(PermissionD.is_forbidden(users[2], groups[0]))
        self.assertTrue(PermissionD.is_forbidden(users[2], groups[1]))
        self.assertTrue(PermissionD.is_accepted(users[2], groups[2]))
        self.assertTrue(PermissionD.is_accepted(users[2], groups[3]))
        self.assertTrue(PermissionD.is_accepted(users[2], groups[4]))
        self.assertTrue(PermissionD.is_forbidden(users[2], users[0]))
        self.assertTrue(PermissionD.is_forbidden(users[2], users[1]))
        self.assertTrue(PermissionD.is_accepted(users[2], users[2]))
        self.assertTrue(PermissionD.is_accepted(users[2], users[3]))
        self.assertTrue(PermissionD.is_accepted(users[2], users[4]))
        pass
