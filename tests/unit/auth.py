from mitama.db import Database
from mitama.db.driver.sqlite3 import get_test_engine

def test_auth():
    db = Database()
    db.set_engine(get_test_engine())
    from mitama.nodes import User
    from mitama.auth import password_auth
    salt = bcrypt.gensalt(prefix = b'2y')
    user = User()
    user.id = 123
    user.name = 'someone'
    user.screen_name = 'somebody'
    user.password = bcrypt.hashpw('somephrase', salt)
    assert password_auth('somebody', 'somephrase')
