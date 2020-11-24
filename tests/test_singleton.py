import random
import unittest

from mitama._extra import _Singleton


class TestSingleton(unittest.TestCase):
    def test_uniqueness(self):
        instanceA = _Singleton()
        instanceB = _Singleton()
        self.assertEqual(instanceA, instanceB)

    def test_assign(self):
        r = random.randint(0, 100)
        instanceA = _Singleton()
        instanceA.test_number = r
        instanceB = _Singleton()
        self.assertEqual(instanceA.test_number, instanceB.test_number)

    def test_extend(self):
        class Singletoned(_Singleton):
            test_number = random.randint(100, 200)

        r = random.randint(0, 100)
        instanceA = Singletoned()
        instanceA.test_number = r
        instanceB = Singletoned()
        self.assertEqual(instanceA.test_number, instanceB.test_number)
