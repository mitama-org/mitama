from mitama.db import BaseDatabase
from mitama.models import permission
# from mitama.db.types import *


class Database(BaseDatabase):
    pass


db = Database()

Permission = permission(db, [
    {
        "name": "test",
        "screen_name": "test"
    }
])

db.create_all()
