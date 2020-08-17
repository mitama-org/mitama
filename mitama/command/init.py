#!/usr/bin/python
'''プロジェクト作成コマンド

    * mitama.json置くだけのコマンド

'''
import os
from pathlib import Path

def init_project_dir(path):
    with open(path / 'mitama.json', mode = 'w') as f:
        conf = Config()
        data = conf.to_dict()
        json_text = json.dumps(data)
        f.write(json_text)

class Command:
    def handle(self, argv = None):
        path = Path(os.getcwd())
        init_project_dir(path)
