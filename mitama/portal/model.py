from base64 import b64encode

import magic

from mitama.db import BaseDatabase
from mitama.db.types import *
from mitama.models import Group, User, permission


db = BaseDatabase(prefix='portal')


class Invite(db.Model):
    icon = Column(LargeBinary)
    screen_name = Column(String)
    email = Column(String)
    name = Column(String)
    token = Column(String, unique=True)
    editable = Column(Boolean)

    def icon_to_dataurl(self):
        f = magic.Magic(mime=True, uncompress=True)
        mime = f.from_buffer(self.icon)
        return "data:" + mime + ";base64," + b64encode(self.icon).decode()

db.create_all()
