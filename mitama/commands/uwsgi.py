#!/usr/bin/python
"""サーバー起動コマンド

ポート番号を引数に取ってHTTPサーバーを起動するコマンド
実行されてないマイグレーションもこいつが実行する
"""

import os
import shutil
from pathlib import Path


class Command:
    def handle(self, argv=None):
        project_dir = Path(os.getcwd())
        src = Path(os.path.dirname(__file__)) / "../skeleton/uwsgi.py"
        shutil.copy(src, project_dir / "uwsgi.py")
