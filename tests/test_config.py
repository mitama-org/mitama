import json
import os
import unittest
from pathlib import Path

from mitama.conf import Config, get_from_project_dir


class TestConfig(unittest.TestCase):
    def test_initialize(self):
        conf = Config(
            Path(os.path.dirname(__file__)) / "test_apps", {"password_validation": {}, "a": "alice", "b": "bob"}
        )
        self.assertEqual(
            conf._project_dir, Path(os.path.dirname(__file__)) / "test_apps"
        )
        self.assertEqual(
            conf._sqlite_db_path,
            Path(os.path.dirname(__file__)) / "test_apps/db.sqlite3",
        )
        self.assertEqual(conf.a, "alice")
        self.assertEqual(conf.b, "bob")

    def test_to_dict(self):
        conf = Config(
            Path(os.path.dirname(__file__)) / "test_apps", {"password_validation":{}, "a": "alice", "b": "bob"}
        )
        self.assertEqual(conf.to_dict(), {"password_validation": {}, "a": "alice", "b": "bob"})

    def test_from_project_dir(self):
        p = Path(os.path.dirname(__file__)) / "test_apps"
        os.chdir(p)
        conf = get_from_project_dir()
        with open(p / "mitama.json") as f:
            d = json.loads(f.read())
            conf_ = Config(p, d)
        self.assertEqual(conf.__dict__, conf_.__dict__)
