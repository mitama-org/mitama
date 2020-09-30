import os
from pathlib import Path
from .controller import *
from .middleware import *
from mitama.app import App as BaseApp, Router, StaticFileController
from mitama.app.method import *
from mitama.app.middlewares import SessionMiddleware
from .model import UpdateUserPermission, CreateUserPermission, DeleteUserPermission, CreateGroupPermission, UpdateGroupPermission, DeleteGroupPermission, Admin

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

class App(BaseApp):
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
    def view(self):
        view = super().view
        view.globals.update(
            user_create_permission = CreateUserPermission.is_accepted,
            user_update_permission = UpdateUserPermission.is_accepted,
            user_delete_permission = DeleteUserPermission.is_accepted,
            group_create_permission = CreateGroupPermission.is_accepted,
            group_update_permission = UpdateGroupPermission.is_accepted,
            group_delete_permission = DeleteGroupPermission.is_accepted,
            is_admin = Admin.is_accepted
        )
        return view
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
                post('/groups/<id>/append', groups.append),
                view('/groups/<id>/remove/<cid>', groups.remove),
                view('/groups/<id>/accept/<cid>/update', groups.accept),
                view('/groups/<id>/forbit/<cid>/update', groups.forbit),
                view('/groups/<id>/settings', groups.update),
                view('/groups/<id>/delete', groups.delete),
                view('/apps', apps.list),
                view('/apps/settings', apps.update),
            ], middlewares = [
                init_mid,
                sess_mid
            ])
        ])
    def delete_user(self, user):
        CreateUserPermission.forbit(user)
        UpdateUserPermission.forbit(user)
        DeleteUserPermission.forbit(user)
        CreateGroupPermission.forbit(user)
        UpdateGroupPermission.forbit(user)
        DeleteGroupPermission.forbit(user)
    def delete_group(self, group):
        CreateUserPermission.forbit(group)
        UpdateUserPermission.forbit(group)
        DeleteUserPermission.forbit(group)
        CreateGroupPermission.forbit(group)
        UpdateGroupPermission.forbit(group)
        DeleteGroupPermission.forbit(group)
    pass

