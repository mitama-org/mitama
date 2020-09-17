from mitama.db.types import *
from mitama.db import BaseDatabase

class Database(BaseDatabase):
    pass

db = Database()

class Invite(db.Model):
    __tablename__ = 'mitama_invite'
    id = Column(Integer, primary_key = True)
    screen_name = Column(String)
    name = Column(String)
    name = Column(String)
