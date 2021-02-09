#!/usr/bin/python
"""型定義

    * ノリで書いたから自分でもよくわからないけど、データベースのカスタム型を定義してみた
    * イメージとしては、データベースの実体には各モデルのidプロパティが入る
    * 取り出すときは数字からそれに対応するモデルのインスタンスが還ってくる
    * 当然、↓のコードはUser.getなんて関数は用意してないので動かないと思われ

"""

from sqlalchemy import *
from sqlalchemy.types import TypeDecorator


class User(TypeDecorator):
    impl = Integer

    def process_bind_param(self, value, dialect):
        if value == None:
            return None
        elif value.__class__.__name__ == "User":
            return value._id
        else:
            return value

    def process_result_value(self, value, dialect):
        from mitama.models import User

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
        elif value.__class__.__name__ == "Group":
            return value._id
        else:
            return value

    def process_result_value(self, value, dialect):
        from mitama.models import Group

        if value == None:
            return None
        else:
            group = Group.retrieve(value)
            return group


class Node(TypeDecorator):
    impl = Integer

    def process_bind_param(self, value, dialect):
        if value.__class__.__name__ == "Group" or value.__class__.__name__ == "User":
            return value._id
        elif type(value) == str and value.split("-")[0] in ["user", "group"]:
            return value
        else:
            raise TypeError("Appending object must be Group or User instance")

    def process_result_value(self, value, dialect):
        prefix = value.split("-")[0]
        if prefix == "user":
            from mitama.models import User

            node = User.retrieve(value)
        elif prefix == "group":
            from mitama.models import Group

            node = Group.retrieve(value)
        else:
            raise TypeError("Invalid ID format")
        return node
