from mitama.db import _CoreDatabase
from mitama.db.driver.sqlite3 import get_test_engine
from sqlalchemy import *
from sqlalchemy.orm import *
from datetime import datetime

def create_test_db():
    engine = get_test_engine()
    return engine

def create_session(engine):
    session = scoped_session(
        sessionmaker(
            autocommit = False,
            autoflush = False,
            bind = engine
        )
    )
    return session

def test_model():
    engine = create_test_db()
    db = _CoreDatabase(engine)
    class Todo(db.Model):
        __tablename__ = 'test_todo'
        title = Column(String(255))
        description = Column(String(255))
        datetime = Column(DateTime)
    db.create_all()
    session = create_session(engine)
    session.execute('insert into test_todo (_id, title, description, datetime) values (123, "test todo", "this is the test", datetime("2020-08-04 12:00:00"))')
    test_todo = Todo.query.first()
    assert test_todo._id == 123
    assert test_todo.title == 'test todo'
    assert test_todo.description == 'this is the test'
    assert test_todo.datetime == datetime(2020, 8, 4, 12)
