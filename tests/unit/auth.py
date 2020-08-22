from mitama.db import Database
from mitama.db.driver.sqlite3 import get_test_engine
import bcrypt

def test_auth():
    db = Database()
    db.set_engine(get_test_engine())
    from mitama.nodes import User
    from mitama.auth import password_auth
    db.create_all()
    salt = bcrypt.gensalt(prefix = b'2a')
    user = User()
    user.id = 123
    user.name = 'someone'
    user.screen_name = 'somebody'
    user.password = bcrypt.hashpw('somephrase'.encode(), salt)
    db.session.add(user)
    db.session.commit()
    assert password_auth('somebody', 'somephrase')
    try:
        password_auth('somebody', 'anyphrase')
        result = True
    except:
        result = False
    assert not result
