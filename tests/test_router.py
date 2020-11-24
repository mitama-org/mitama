import unittest
from wsgiref.util import setup_testing_defaults

from mitama.app import Controller, Router
from mitama.app.http import Request
from mitama.app.method import *


class TestRouter(unittest.TestCase):
    def test_router(self):
        environ = {}
        setup_testing_defaults(environ)
        request = Request(environ)

        class TestController(Controller):
            def handle(self, request):
                return "dadada"

        router = Router([view("/", TestController)])
        request_, handle, method = router.match(request)
        self.assertTrue(callable(handle))
