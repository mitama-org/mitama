import unittest
from mitama.app.forms import *

class AForm(Form):
    screen_name = Field(label="ログイン名", required=True)
    email = Field(label="メールアドレス", regex=r"([\w]+)@([\w\.\-\_]+)")
    name = Field(label="名前")


class TestForm(unittest.TestCase):
    def test_form(self):
        form = AForm({
            "screen_name": "hogehoge",
            "name": "hoge"
        })
        self.assertEqual(form["screen_name"], "hogehoge")
        self.assertEqual(form["name"], "hoge")

    def test_required(self):
        with self.assertRaises(EmptyError):
            form = AForm({
                "name": "hoge"
            })

    def test_regex(self):
        with self.assertRaises(FormatError):
            form = AForm({
                "screen_name": "hoge",
                "email" :"hoge"
            })
        form = AForm({
                "screen_name": "hoge",
                "email" :"hoge@hoge"
            })
        self.assertEqual(form["email"], "hoge@hoge")
