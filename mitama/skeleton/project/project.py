#!/usr/bin/python

"""
uwsgi --http=0.0.0.0:8080 --wsgi-file=/path/to/this --callable=app.wsgi
"""
import os

from mitama.app import Project, include


application = Project(
    include(mitama.portal, path="/"),
    project_dir = Path(os.path.dirname(__file__)),
    database = {
        "type":"sqlite",
        "host":"localhost",
        "name":"mitama",
        "user":"mitama",
        "password":"mitama",
    }
)


if __name__ == "__main__":
    application.command()
