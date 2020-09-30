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
        if value == None:
            return None
        else:
            return value._id
    def process_result_value(self, value, dialect):
        from mitama.nodes import User
        if value == None:
            return None
        else:
            user = User.retrieve(value)
            return user

class Group(TypeDecorator):
    impl = Integer
    def process_bind_param(self, value, dialect):
        if value == None:
            return None
        else:
            return value._id
    def process_result_value(self, value, dialect):
        from mitama.nodes import Group
        if value == None:
            return None
        else:
            group = Group.retrieve(value)
            return group

class Node(TypeDecorator):
    impl = Integer
    def process_bind_param(self, value, dialect):
        if value.__class__.__name__ == 'Group':
            return value._id * 2
        elif value.__class__.__name__ == 'User':
            return value._id * 2 - 1
        else:
            raise TypeError('Appending object must be Group or User instance')
    def process_result_value(self, value, dialect):
        if value % 2 == 1:
            from mitama.nodes import User
            node = User.retrieve((value + 1) / 2)
        else:
            from mitama.nodes import Group
            node = Group.retrieve(value / 2)
        return node
