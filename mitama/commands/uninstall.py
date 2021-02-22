#!/usr/bin/python

import os, sys
import shutil
import argparse
import json
import importlib
from pathlib import Path


class Command:
    def handle(self, argv=None):
        conf = get_from_project_dir()
        try:
            app_name = argv[0]
        except IndexError:
            app_name = input("App name: ")

        current_dir = os.getcwd()
        sys.path.append(current_dir)
        if app_name not in sys.modules:
            init = importlib.__import__(app_name, fromlist=["AppBuilder"])
        else:
            init = importlib.reload(app_name)

        init.uninstall(app_name)
        del conf.apps[app_name]
        json_data = json.dumps(conf.to_dict())
        with open("mitama.json" ,"w") as f:
            f.write(json_data)
