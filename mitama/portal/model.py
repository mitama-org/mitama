from mitama.db.types import *
from mitama.db import BaseDatabase
from base64 import b64encode
import magic

class Database(BaseDatabase):
    pass

db = Database()

class Invite(db.Model):
    __tablename__ = 'mitama_invite'
    id = Column(Integer, primary_key = True)
    icon = Column(LargeBinary)
    screen_name = Column(String)
    name = Column(String)
    token = Column(String, unique = True)
    def icon_to_dataurl(self):
        f = magic.Magic(mime = True, uncompress = True)
        mime = f.from_buffer(self.icon)
        return 'data:'+mime+';base64,'+b64encode(self.icon).decode()
    @classmethod
    def retrieve(cls, id):
        return cls.query.filter(cls.id == id).first()


db.create_all()
