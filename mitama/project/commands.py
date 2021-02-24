import os
import sys
import importlib
from mitama.app import AppRegistry
from mitama.app.http import run_app


def run(project, args):
    port = args.port
    project.port = port
    run_app(project, project.port)
