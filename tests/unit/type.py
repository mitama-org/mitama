from mitama.db import _CoreDatabase
from mitama.db.driver.sqlite3 import get_test_engine
from sqlalchemy.orm import *
from mitama.db import types
from mitama.db.types import Column
from pprint import pprint

def create_test_db():
    engine = get_test_engine()
    return engine

def test_nodes():
    engine = create_test_db()
    db = _CoreDatabase(engine)
    from mitama.nodes import User, Group
    class Profile(db.Model):
        __tablename__ = 'test_profile'
        description = Column(types.String(255))
        user = Column(types.User)
    class GroupProfile(db.Model):
        __tablename__ = 'test_group_profile'
        description = Column(types.String(255))
        group = Column(types.Group)
    db.create_all()
    test_user = User()
    test_user.name = 'test'
    test_user.screen_name = 'testuser'
    test_user.password = 'testpass'
    db.session.add(test_user)
    test_group= Group()
    test_group.name = 'test'
    test_group.screen_name = 'testgroup'
    db.session.add(test_group)
    db.session.commit()
    test_user_profile = Profile()
    test_user_profile.description = 'this is the test user'
    test_user_profile.user = test_user
    db.session.add(test_user_profile)
    test_group_profile = GroupProfile()
    test_group_profile.description = 'this is the test group'
    test_group_profile.group = test_group
    db.session.add(test_group_profile)
    db.session.commit()
    test_user_profile_ = Profile.query.first()
    test_group_profile_ = GroupProfile.query.first()
    assert test_user_profile_.user.name == test_user.name
    assert test_user_profile_.user.screen_name == test_user.screen_name
    assert test_user_profile_.user.password == test_user.password
    assert test_group_profile_.group.name == test_group.name
    assert test_group_profile_.group.screen_name == test_group.screen_name
