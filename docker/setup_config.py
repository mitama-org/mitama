#!/usr/bin/env python
import json
import os

with open('/project/mitama.json') as f:
    data = f.read()

data_json = json.load(data)
data_json["database"] = {}

if os.environ["DATABASE_TYPE"] == "sqlite3":
    data_json["database"]["type"] = "sqlite3"
    data_json["database"]["path"] = "/project/db.sqlite3"
elif os.environ["DATABASE_TYPE"] == "mysql":
    data_json["database"]["type"] = "mysql"
    data_json["database"]["host"] = os.environ["DATABASE_HOST"]
    data_json["database"]["name"] = os.environ["DATABASE_NAME"]
    data_json["database"]["user"] = os.environ["DATABASE_USER"]
    data_json["database"]["password"] = os.environ["DATABASE_PASSWORD"]
elif os.environ["DATABASE_TYPE"] == "postgresql":
    data_json["database"]["type"] = "postgresql"
    data_json["database"]["host"] = os.environ["DATABASE_HOST"]
    data_json["database"]["name"] = os.environ["DATABASE_NAME"]
    data_json["database"]["user"] = os.environ["DATABASE_USER"]
    data_json["database"]["password"] = os.environ["DATABASE_PASSWORD"]

with open('/project/mitama.json', 'w') as f:
    f.write(json.dumps(data_json))
