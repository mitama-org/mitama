#!/usr/bin/python
"""プロジェクト作成コマンド

    * mitama.json置くだけのコマンド

"""
import os
import shutil
from pathlib import Path

from mitama.conf import Config


def init_project_dir(path):
    src = Path(os.path.dirname(__file__)) / "../skeleton/project"
    shutil.copytree(src, path, symlinks=False)


class Command:
    def handle(self, argv=None):
        path = Path(os.getcwd())
        init_project_dir(path)
