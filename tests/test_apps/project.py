#!/usr/bin/python

"""
uwsgi --http=0.0.0.0:8080 --wsgi-file=/path/to/this --callable=app.wsgi
"""
import os

from mitama.project import Project, include
from mitama.db import DatabaseManager

project_dir = os.path.dirname(os.path.abspath(__file__))

DatabaseManager({
    "type":"sqlite",
    "path": project_dir+'/db.sqlite3',
    #"host":"localhost",
    #"name":"mitama",
    #"user":"mitama",
    #"password":"mitama",
})

project = Project(
    include("mitama.portal", path="/"),
    include("hello", path="/hel"),
    project_dir = project_dir,
    vapid = {
        "public_key": "BBE84JBBsED5HMkkKspKFxf-1UcQfd3VXATjghJD3Gr0u2ewBcxmCpQFuRgs4vQeFknJeoler61xxiOyfXACakQ",
        "private_key": "1whN4CfJiPqNCfpG7xpLue_evaWuZnlKdqbSqKoWnbs",
        "mailto": "mitama@example.com"
    }
)
application = project.wsgi


if __name__ == "__main__":
    project.command()
