#!/usr/bin/python
'''パスワード認証

    * Mitamaではパスワードのハッシュ化にはBCRYPTアルゴリズムの$2yプリフィクスのものを利用します
    * 理由は、前回バージョンの第三版がPHPのpassword_hash関数を使用しており、移植性を保ちたかったからです。
    * しょうもなくてすみません
'''

import bcrypt
from mitama.nodes import User

class AuthorizationError(Exception):
    pass

def password_auth(screen_name, password):
    user = User.query.filter(User.screen_name == screen_name).first()
    if bcrypt.checkpw(password.encode(), user.password):
        return user
    else:
        raise AuthorizationError('Wrong password')
