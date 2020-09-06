from mitama.app import BaseMetadata
from mitama.db import get_app_engine, Database as BaseDatabase

class Metadata(BaseMetadata):
    pass

class Database(BaseDatabase):
    def __init__(self, engine = None):
        super().__init__()
        meta = Metadata()
        if self.engine == None:
            if engine == None:
                self.set_engine(get_app_engine(meta.name))
            else:
                self.set_engine(engine)

def init_app(name):
    meta = Metadata()
    meta.name = name