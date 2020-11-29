import unittest

from mitama.db import _CoreDatabase

db = _CoreDatabase.test()

from mitama.models import User


class TestUser(unittest.TestCase):
    def test_user(self):
        user = User()
        user.name = "alice"
        user.screen_name = "alice"
        user.set_password("alice_s_password_1234")
        user.create()
        self.assertTrue(User.password_auth("alice", "alice_s_password_1234"))
        jwt = user.get_jwt()
        self.assertEqual(User.check_jwt(jwt), user)
