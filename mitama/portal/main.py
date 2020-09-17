import os
from pathlib import Path
from .controller import *
from .middleware import *
from mitama.app import App, Router
from mitama.app.method import *
from mitama.app.middlewares import SessionMiddleware

import urllib

home = HomeController()
reg = RegisterController()
users = UsersController()
groups = GroupsController()
init_mid = InitializeMiddleware()
sess_mid = SessionMiddleware()

class App(App):
    instances = [
        home,
        reg,
        users,
        groups,
        init_mid,
        sess_mid
    ]
    def router(self):
        return Router([
            static('/assets', self.project_dir / 'static'),
            view('/setup', reg.setup),
            view('/signup', reg.signup),
            Router([
                view('/', home),
                view('/users', users.list),
                view('/users/invite', users.create),
                view('/users/{id}', users.retrieve),
                view('/users/{id}/settings', users.update),
                view('/users/{id}/delete', users.delete),
                view('/groups', groups.list),
                view('/groups/create', groups.create),
                view('/groups/{id}', groups.retrieve),
                view('/groups/{id}/settings', groups.update),
                view('/groups/{id}/delete', groups.delete),
            ], middlewares = [
                init_mid,
                sess_mid
            ])
        ])
    pass

