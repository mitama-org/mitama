import unittest

from mitama.app import HookRegistry
from mitama.db import _CoreDatabase

db = _CoreDatabase.test()

from mitama.models import Group, User


class TestHook(unittest.TestCase):
    def test_hook(self):
        hooks = HookRegistry()
        user = User()
        group = Group()

        class TestError(Exception):
            pass

        def cu(user):
            raise TestError("hello")

        def uu(user):
            raise TestError("hello")

        def du(user):
            raise TestError("hello")

        def cg(group):
            raise TestError("hello")

        def ug(group):
            raise TestError("hello")

        def dg(group):
            raise TestError("hello")

        hooks.add_create_user_hook(cu)
        hooks.add_update_user_hook(uu)
        hooks.add_delete_user_hook(du)
        hooks.add_create_group_hook(cg)
        hooks.add_update_group_hook(ug)
        hooks.add_delete_group_hook(dg)
        self.assertRaises(TestError, hooks.create_user, user)
        self.assertRaises(TestError, hooks.update_user, user)
        self.assertRaises(TestError, hooks.delete_user, user)
        self.assertRaises(TestError, hooks.create_group, group)
        self.assertRaises(TestError, hooks.update_group, group)
        self.assertRaises(TestError, hooks.delete_group, group)
        hooks.create_user_hooks = list()
        hooks.update_user_hooks = list()
        hooks.delete_user_hooks = list()
        hooks.create_group_hooks = list()
        hooks.update_group_hooks = list()
        hooks.delete_group_hooks = list()
