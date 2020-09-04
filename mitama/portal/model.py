from mitama.db.types import *
from . import Database

db = Database()

class Invite(db.Model):
    __tablename__ = 'mitama_invite'
    id = Column(Integer, primary_key = True)
    screen_name = Column(String)
    name = Column(String)
    name = Column(String)
