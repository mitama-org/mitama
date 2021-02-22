import io
import unittest
from wsgiref.util import request_uri, setup_testing_defaults

from mitama.app.http import Request, Response


class TestHttp(unittest.TestCase):
    def test_request(self):
        environ = {"QUERY_STRING": "foo=bar&hoge=piyo"}
        setup_testing_defaults(environ)
        req = Request(environ)
        self.assertEqual(req.scheme, "http")
        self.assertEqual(req.host, environ["HTTP_HOST"])
        self.assertEqual(req.method, environ["REQUEST_METHOD"])
        self.assertEqual(req.raw_path, "/?foo=bar&hoge=piyo")
        self.assertEqual(req.path, "/")
        self.assertEqual(req.query, {"foo": ["bar"], "hoge": ["piyo"]})
        self.assertEqual(req.version, environ["SERVER_PROTOCOL"])
        self.assertEqual(req.url, request_uri(environ))

    def test_response(self):
        res = Response(
            text="Hello, world!",
            headers={
                "hoge": "piyo",
                "foo": "bar",
                "huga": "hogehuga",
            },
            status=200,
            reason="OK",
            content_type="text/html",
            charset="utf-8",
        )

        def start_response(state, headers):
            nonlocal self
            self.assertEqual(state, "200 OK")
            self.assertEqual(
                headers,
                [
                    ("hoge", "piyo"),
                    ("foo", "bar"),
                    ("huga", "hogehuga"),
                    ("Content-Type", "text/html"),
                ],
            )

        output = res.start(None, start_response)
        self.assertEqual(output, [b"Hello, world!"])
