#!/usr/bin/python

import os
from mitama.app import _MainApp, AppRegistry

PROJECT_DIR = os.path.dirname(__file__)
os.chdir(PROJECT_DIR)
app_registry = AppRegistry()
app_registry.load_config()
app = _MainApp(app_registry)

def application(env, start_response):
    return app.wsgi(env, start_response)

