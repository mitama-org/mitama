#!/usr/bin/python
'''パスワード認証

Mitamaではパスワードのハッシュ化にはBCRYPTアルゴリズムの$2yプリフィクスのものを利用します
理由は、前回バージョンの第三版がPHPのpassword_hash関数を使用しており、移植性を保ちたかったからです。
しょうもなくてすみません
'''

import bcrypt
import jwt
import random
import secrets
import hashlib
import base64
from mitama.nodes import User

secret = secrets.token_hex(32)

class AuthorizationError(Exception):
    pass

def password_auth(screen_name, password):
    '''ログイン名とパスワードで認証します

    :param screen_name: ログイン名
    :param password: パスワード
    :return: Userインスタンス
    '''
    user = User.query.filter(User.screen_name == screen_name).first()
    password = base64.b64encode(
        hashlib.sha256(
            password.encode() * 10
        ).digest()
    )
    if bcrypt.checkpw(password, user.password):
        return user
    else:
        raise AuthorizationError('Wrong password')

def password_hash(password):
    '''パスワードをハッシュ化します

    :param password: パスワードのプレーンテキスト
    :return: パスワードハッシュ
    '''
    salt = bcrypt.gensalt()
    password = base64.b64encode(
        hashlib.sha256(
            password.encode() * 10
        ).digest()
    )
    return bcrypt.hashpw(password, salt)

def get_jwt(user):
    '''UserインスタンスからJWTを生成します

    :param user: Userインスタンス
    :return: JWT
    '''
    nonce = ''.join([str(random.randint(0,9)) for i in range(16)])
    result = jwt.encode(
        {
            'id': user._id,
            'nonce': nonce
        },
        secret,
        algorithm='HS256'
    )
    return result.decode()

def check_jwt(token):
    '''JWTからUserインスタンスを取得します

    :param token: JWT
    :return: Userインスタンス
    '''
    try:
        result = jwt.decode(
            token,
            secret,
            algorithm='HS256'
        )
    except jwt.exceptions.InvalidTokenError as err:
        raise AuthorizationError('Invalid token.')
    return User.query.filter(User._id == result['id']).first()
