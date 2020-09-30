from mitama.db import _Database
from mitama.db.driver.sqlite3 import get_test_engine
import bcrypt

def test_auth():
    db = _Database()
    db.set_engine(get_test_engine())
    from mitama.nodes import User
    from mitama.auth import password_hash, password_auth
    db.create_all()
    user = User()
    user._id = 123
    user.name = 'someone'
    user.screen_name = 'somebody'
    user.password = password_hash('somephrase')
    db.session.add(user)
    db.session.commit()
    assert password_auth('somebody', 'somephrase')
    try:
        password_auth('somebody', 'anyphrase')
        result = True
    except:
        result = False
    assert not result

def test_jwt():
    from mitama.nodes import User
    from mitama.auth import get_jwt, check_jwt
    user = User.query.first()
    assert check_jwt(get_jwt(user)) == user
