import os
from pathlib import Path
from .controller import *
from .middleware import *
from mitama.app import App as BaseApp, Router, static_files
from mitama.app.method import *
from mitama.app.middlewares import SessionMiddleware
from .model import UpdateUserPermission, CreateUserPermission, DeleteUserPermission, CreateGroupPermission, UpdateGroupPermission, DeleteGroupPermission, Admin

import urllib

with open(Path(os.path.dirname(__file__)) / 'static/icon.png', 'rb') as f:
    icon = f.read()

class App(BaseApp):
    name = "Mitama Portal"
    description = "Mitamaのアプリポータルです。他のアプリを確認できる他、配信の設定やグループの編集、ユーザーの招待ができます。"
    icon = icon
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
            view('/static/<path:path>', static_files()),
            view('/setup', RegisterController, 'setup'),
            view('/signup', RegisterController, 'signup'),
            view('/login', SessionController, 'login'),
            Router([
                view('/', GroupsController, 'list'),
                view('/logout', SessionController, 'logout'),
                view('/users', UsersController, 'list'),
                view('/users/invite', UsersController, 'create'),
                view('/users/invite/<id>/delete', UsersController, 'cancel'),
                view('/users/<id>', UsersController, 'retrieve'),
                view('/users/<id>/settings', UsersController, 'update'),
                view('/users/<id>/delete', UsersController, 'delete'),
                view('/groups', GroupsController, 'list'),
                view('/groups/create', GroupsController, 'create'),
                view('/groups/<id>', GroupsController, 'retrieve'),
                post('/groups/<id>/append', GroupsController, 'append'),
                view('/groups/<id>/remove/<cid>', GroupsController, 'remove'),
                view('/groups/<id>/accept/<cid>/update', GroupsController, 'accept'),
                view('/groups/<id>/forbit/<cid>/update', GroupsController, 'forbit'),
                view('/groups/<id>/settings', GroupsController, 'update'),
                view('/groups/<id>/delete', GroupsController, 'delete'),
                view('/apps', AppsController, 'list'),
                view('/apps/settings', AppsController, 'update'),
            ], middlewares = [
                InitializeMiddleware,
                SessionMiddleware
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

