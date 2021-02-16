#!/usr/bin/python
"""プロジェクト作成コマンド

    * mitama.json置くだけのコマンド

"""
import os
import shutil
import glob
from pathlib import Path

from mitama.conf import Config


def init_project_dir(path):
    files = glob.glob(os.path.dirname(__file__) + "/../skeleton/project/*")
    for file in files:
        if os.path.isdir(file):
            continue
        shutil.copy(file, path, follow_symlinks=False)


class Command:
    def handle(self, argv=None):
        path = Path(os.getcwd())
        init_project_dir(path)
