import unittest
from mitama.app.registry import AppRegistry

def match(path, reg):
    for app_path, app in reg.items():
        if app_path[0] != "/":
            app_path = "/" + app_path
        if path.startswith(app_path):
            return app

class TestRegistry(unittest.TestCase):
    def test_routing(self):
        reg = AppRegistry()
        reg['/hoge'] = 'hoge'
        reg['/'] = 'piyo'
        reg['/hoge/foo'] = 'foo'
        reg['/hoge/bar'] = 'bar'
        self.assertEqual(match('/', reg), 'piyo')
        self.assertEqual(match('/hoge', reg), 'hoge')
        self.assertEqual(match('/hoge/foo', reg), 'foo')
        self.assertEqual(match('/hoge/bar', reg), 'bar')
