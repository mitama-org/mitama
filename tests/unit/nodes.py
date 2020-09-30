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
    session.execute('insert into mitama_user (_id, name, screen_name, password) values (123, "test_user", "test_user_screen", "test_user_password")')
    session.execute('insert into mitama_group (_id, name, screen_name) values (456, "test_group", "test_group_screen")')
    test_user = User.query.first()
    test_group = Group.query.first()
    assert test_user._id == 123
    assert test_user.name == 'test_user'
    assert test_user.screen_name == 'test_user_screen'
    assert test_user.password == 'test_user_password'
    assert test_group._id == 456
    assert test_group.name == 'test_group'
    assert test_group.screen_name == 'test_group_screen'

def test_relation():
    db = _CoreDatabase()
    from mitama.nodes import User,Group,Relation
    db.create_all()
    test_user = User()
    test_user.name = 'test_user_'
    test_user.screen_name = 'test_user_screen_'
    test_user.password = 'test_pass_'
    db.session.add(test_user)
    test_group = Group()
    test_group.name = 'test_group_'
    test_group.screen_name = 'test_group_screen_'
    test_group2 = Group()
    test_group2.name = 'test_group_2'
    test_group2.screen_name = 'test_group_screen_2'
    db.session.add(test_group)
    db.session.add(test_group2)
    db.session.commit()
    test_group.append_all([
        test_user,
        test_group2
    ])
    test_children = test_group.children()
    assert test_children[0] == test_user
    assert test_children[1] == test_group2
    test_group.remove(test_user)
    test_group.remove(test_group2)
    test_children = test_group.children()
    assert len(test_children) == 0

def test_relation():
    db = _CoreDatabase()
    from mitama.nodes import User,Group,Relation
    db.create_all()
    test_user = User()
    test_user.name = 'test_user_'
    test_user.screen_name = 'test_user_screen_'
    test_user.password = 'test_pass_'
    db.session.add(test_user)
    test_group = Group()
    test_group.name = 'test_group_'
    test_group.screen_name = 'test_group_screen_'
    test_group2 = Group()
    test_group2.name = 'test_group_2'
    test_group2.screen_name = 'test_group_screen_2'
    db.session.add(test_group)
    db.session.add(test_group2)
    db.session.commit()
    test_group.append_all([
        test_user,
        test_group2
    ])
    test_children = test_group.children()
    assert test_children[0] == test_user
    assert test_children[1] == test_group2
    test_group.remove(test_user)
    test_group.remove(test_group2)
    test_children = test_group.children()
    assert len(test_children) == 0

def test_crud():
    db = _CoreDatabase()
    from mitama.nodes import User,Group
    test_user = User()
    test_user.name = 'test_user__'
    test_user.screen_name = 'test_user_screen__'
    test_user.password = 'test_pass__'
    test_user.create()
    searched = User.query.filter(User.screen_name == 'test_user_screen__').first()
    assert test_user == searched
    test_user.name = 'test_user_changed'
    test_user.update()
    searched = User.query.filter(User.screen_name == 'test_user_screen__').first()
    assert test_user == searched
    test_user.delete()
    searched = User.query.filter(User.screen_name == 'test_user_screen__').all()
    assert len(searched) == 0


