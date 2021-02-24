#!/usr/bin/python

"""
uwsgi --http=0.0.0.0:8080 --wsgi-file=/path/to/this --callable=app.wsgi
"""
import os

from mitama.project import Project, include
from mitama.db import DatabaseManager

project_dir = os.path.dirname(__file__)

DatabaseManager({
    "type":"sqlite",
    "path": project_dir+'/db.sqlite3',
    #"host":"localhost",
    #"name":"mitama",
    #"user":"mitama",
    #"password":"mitama",
})

application = Project(
    include("mitama.portal", path="/"),
    project_dir = project_dir
)


if __name__ == "__main__":
    application.command()