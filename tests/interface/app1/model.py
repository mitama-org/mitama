from mitama.db.types import *
from . import Database

db = Database()

class Some(db.Model):
    __tablename__ = 'app1_sometable'
    id = Column(Integer, primary_key = True)

db.create_all()


