#!/usr/bin/python
"""コマンド定義

    * 1ファイル1コマンドでクラスとして書いてます
    * handleがコマンドライン引数の引数部を受け取って実行する
    * 抽象化はするかどうか迷ってる（Pythonで抽象化がどれくらい尊いものかよくわかんない）
    * argparseを入れようか迷ったけど、位置引数しか必要に成る予定が無いのでとりあえず入れてない
"""

import importlib
import sys
import argparse
import os
import shutil
import glob
import pkg_resources
from pathlib import Path


def init_project_dir(path):
    files = glob.glob(os.path.dirname(__file__) + "/skeleton/project/*")
    for file in files:
        if os.path.isdir(file):
            continue
        shutil.copy(file, path, follow_symlinks=False)


def init(args):
    path = Path(os.getcwd())
    init_project_dir(path)

def mkapp(args):
    try:
        project_name = argv[0]
    except IndexError:
        raise IndexError("No app name given to command arguments.")
    current_dir = Path(os.getcwd())
    project_dir = current_dir / project_name
    src = Path(os.path.dirname(__file__)) / "../skeleton/app_templates"
    shutil.copytree(src, project_dir, symlinks=False)

def new(args):
    try:
        project_name = argv[0]
    except IndexError:
        raise IndexError("No project name given to command arguments.")
    current_dir = Path(os.getcwd())
    project_dir = current_dir / project_name
    os.mkdir(project_dir)
    init_project_dir(project_dir)

def version(args):
    v = pkg_resources.get_distribution("mitama").version
    print(v)

