from mitama.db import _CoreDatabase
from mitama.db.driver.sqlite3 import get_test_engine
from sqlalchemy import *
from sqlalchemy.orm import *

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

def test_nodes():
    engine = create_test_db()
    db = _CoreDatabase(engine)
    from mitama.nodes import User, Group
    db.create_all()
    session = create_session(engine)
    session.execute('insert into mitama_user (id, name, screen_name, password) values (123, "test_user", "test_user_screen", "test_user_password")')
    session.execute('insert into mitama_group (id, name, screen_name) values (456, "test_group", "test_group_screen")')
    test_user = User.query.first()
    test_group = Group.query.first()
    assert test_user.id == 123
    assert test_user.name == 'test_user'
    assert test_user.screen_name == 'test_user_screen'
    assert test_user.password == 'test_user_password'
    assert test_group.id == 456
    assert test_group.name == 'test_group'
    assert test_group.screen_name == 'test_group_screen'
