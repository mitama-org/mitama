#!/usr/bin/python

from mitama.conf import get_from_project_dir
from sqlalchemy import scoped_session, sessionmaker

class Singleton:
    def __new__(cls, *args, **kargs):
        if not hasattr(cls, '_instance'):
            cls._instance = super(Singleton, cls).__new__(cls)
        return cls._instance

class Database(Singleton):
    engine = None
    session = None
    def load_engine(self, engine):
        self.engine = engine
        self.session = scoped_session(
            sessionmaker(
                autocommit = False,
                autoflush = False,
                bind = engine
            )
        )

