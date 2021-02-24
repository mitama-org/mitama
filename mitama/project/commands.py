import os
import sys
import importlib
from mitama.app import AppRegistry
from mitama.app.http import run_app
from mitama.conf import get_from_project_dir


def run(project, args):
    port = args.port
    project.port = int(port)
    run_app(project, project.port)
