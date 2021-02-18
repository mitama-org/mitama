#!/usr/bin/python

import os, sys
import shutil
import argparse
import json
import importlib
from pathlib import Path
from mitama.conf import get_from_project_dir


class Command:
    def handle(self, argv=None):
        conf = get_from_project_dir()
        try:
            app_name = argv[0]
        except IndexError:
            app_name = input("App name: ")

        current_dir = os.getcwd()
        dirname = os.path.basename(current_dir)
        sys.path.append(current_dir + "/../")
        project = importlib.__import__(dirname, fromlist = ["__project__"]).__project__

        project.install(app_name, path)
        conf.apps[app_name] = {
            "path": path
        }
        json_data = json.dumps(conf.to_dict())
        with open("mitama.json" ,"w") as f:
            f.write(json_data)
