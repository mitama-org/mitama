#!/usr/bin/python

"""
uwsgi --http=0.0.0.0:8080 --wsgi-file=/path/to/this --callable=app.wsgi
"""
import os

from mitama.app import Project

os.chdir(
    os.path.dirname(__file__)
)

__project__ = Project()
