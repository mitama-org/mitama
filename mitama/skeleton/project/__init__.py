#!/usr/bin/python

"""
uwsgi --http=0.0.0.0:8080 --wsgi-file=/path/to/this --callable=app.wsgi
"""
import os

from mitama.app import AppRegistry, _MainApp

os.chdir(
    os.path.dirname(__file__)
)

app_registry = AppRegistry()
app_registry.load_config()
app = _MainApp(app_registry)
