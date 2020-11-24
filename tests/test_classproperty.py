import unittest

from mitama._extra import _classproperty


class TestClassProperty(unittest.TestCase):
    def test_getter(self):
        class ClassA:
            @_classproperty
            def value(cls):
                return "hello, world!"

        self.assertEqual(ClassA.value, "hello, world!")
