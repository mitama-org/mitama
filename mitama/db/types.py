#!/usr/bin/python
'''型定義

    * ノリで書いたから自分でもよくわからないけど、データベースのカスタム型を定義してみた
    * イメージとしては、データベースの実体には各モデルのidプロパティが入る
    * 取り出すときは数字からそれに対応するモデルのインスタンスが還ってくる
    * 当然、↓のコードはUser.getなんて関数は用意してないので動かないと思われ

'''

from sqlalchemy.types import TypeDecorator
from sqlalchemy import *

class User(TypeDecorator):
    impl = Integer
    def process_bind_param(self, value, dialect):
        print('binding...', value, value.id)
        return value.id
    def process_result_value(self, value, dialect):
        from mitama.nodes import User
        user = User.retrieve(value)
        print('retrieved', user)
        return user

class Group(TypeDecorator):
    impl = Integer
    def process_bind_param(self, value, dialect):
        return value.id
    def process_result_value(self, value, dialect):
        from mitama.nodes import Group
        group = Group.retrieve(value)
        print('retrieved', group)
        return group
