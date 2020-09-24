import os
from pathlib import Path
from .controller import *
from .middleware import *
from mitama.app import App, Router, StaticFileController
from mitama.app.method import *
from mitama.app.middlewares import SessionMiddleware

import urllib

#home = HomeController()
sess = SessionController()
reg = RegisterController()
users = UsersController()
groups = GroupsController()
apps = AppsController()
init_mid = InitializeMiddleware()
sess_mid = SessionMiddleware()
static = StaticFileController()

class App(App):
    name = "Mitama Portal"
    description = "Mitamaのアプリポータルです。他のアプリを確認できる他、配信の設定やグループの編集、ユーザーの招待ができます。"
    instances = [
        #home,
        reg,
        sess,
        users,
        groups,
        apps,
        static,
        init_mid,
        sess_mid
    ]
    @property
    def router(self):
        return Router([
            view('/static/<path:path>', static),
            view('/setup', reg.setup),
            view('/signup', reg.signup),
            view('/login', sess.login),
            Router([
                view('/', groups.list),
                view('/logout', sess.logout),
                view('/users', users.list),
                view('/users/invite', users.create),
                view('/users/invite/<id>/delete', users.cancel),
                view('/users/<id>', users.retrieve),
                view('/users/<id>/settings', users.update),
                view('/users/<id>/delete', users.delete),
                view('/groups', groups.list),
                view('/groups/create', groups.create),
                view('/groups/<id>', groups.retrieve),
                view('/groups/<id>/settings', groups.update),
                view('/groups/<id>/delete', groups.delete),
                view('/apps', apps.list),
                view('/apps/settings', apps.update),
            ], middlewares = [
                init_mid,
                sess_mid
            ])
        ])
    pass

