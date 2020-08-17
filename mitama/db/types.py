#!/usr/bin/python
'''型定義

    * ノリで書いたから自分でもよくわからないけど、データベースのカスタム型を定義してみた
    * イメージとしては、データベースの実体には各モデルのidプロパティが入る
    * 取り出すときは数字からそれに対応するモデルのインスタンスが還ってくる
    * 当然、↓のコードはUser.getなんて関数は用意してないので動かないと思われ

'''

from sqlalchemy.types import TypeDecorator, INT

class User(types.TypeDecorator):
    impl = INT
    def process_bind_param(self, value, dialect):
        return value.id
    def process_result_value(self, value, dialect):
        return User.get(value)

class Group(types.TypeDecorator):
    impl = INT
    def process_bind_param(self, value, dialect):
        return value.id
    def process_result_value(self, value, dialect):
        return Group.get(value)
