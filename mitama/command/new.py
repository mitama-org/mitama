#!/usr/bin/python
'''プロジェクト作成コマンド

    * ディレクトリ作ってmitama.json置くだけのコマンド

'''

import os
from pathlib import Path
from .init import init_project_dir

class Command:
    def handle(self, argv = None):
        try:
            project_name = argv[0]
        except IndexError:
            raise IndexError(
                'No project name given to command arguments.'
            )
        current_dir = Path(os.getcwd())
        project_dir = current_dir / project_name
        os.mkdir(project_dir)
        init_project_dir(project_dir)
