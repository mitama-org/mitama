import os
from pathlib import Path
from .controller import *
from .middleware import *
from mitama.app import App as BaseApp, Router, static_files
from mitama.app.method import *
from mitama.app.middlewares import SessionMiddleware
from .model import UpdateUserPermission, CreateUserPermission, DeleteUserPermission, CreateGroupPermission, UpdateGroupPermission, DeleteGroupPermission, Admin
import saml2
from saml2 import BINDING_HTTP_REDIRECT, BINDING_HTTP_POST
from saml2.entity_category.edugain import COC
from saml2.client import Saml2Client
from saml2.saml import NAME_FORMAT_URI

import urllib

try:
    from saml2.sigver import get_xmlsec_binary
except ImportError:
    get_xmlsec_binary = None

if get_xmlsec_binary:
    xmlsec_path = get_xmlsec_binary(["/opt/local/bin","/usr/local/bin"])
else:
    xmlsec_path = '/usr/local/bin/xmlsec1'

with open(Path(os.path.dirname(__file__)) / 'static/icon.png', 'rb') as f:
    icon = f.read()

class App(BaseApp):
    name = "Mitama Portal"
    description = "Mitamaのアプリポータルです。他のアプリを確認できる他、配信の設定やグループの編集、ユーザーの招待ができます。"
    icon = icon
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        SAML_CNF = saml2.config.config_factory('sp', {
            "entityid": "https:"+self.convert_fullurl("/sp.xml"),
            "entity_category": [COC],
            "description": "Example SP",
            "service": {
                "sp": {
                    "want_response_signed": False,
                    "authn_requests_signed": True,
                    "logout_requests_signed": True,
                    "endpoints": {
                        "assertion_consumer_service": [
                            (str(self.convert_url("/acs/post")), BINDING_HTTP_POST)
                        ],
                        "single_logout_service": [
                            (str(self.convert_url("/slo/redirect")), BINDING_HTTP_REDIRECT),
                            (str(self.convert_url("/slo/post")), BINDING_HTTP_POST)
                        ]
                    }
                }
            },
            "key_file": str(self.project_dir / self.config["saml"]["key"]),
            "cert_file": str(self.project_dir / self.config["saml"]["cert"]),
            "xmlsec_binary": xmlsec_path,
            "metadata": {
                "local": [str(self.project_dir / self.config["saml"]["metadata"]["local"])]
            },
            "name_form": NAME_FORMAT_URI
        })
        SP = Saml2Client(config = SAML_CNF)

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
                view('/acs/post<hoge:re:.*>', ACSController, 'post'),
                view('/acs/redirect<hoge:re:.*>', ACSController, 'redirect'),
                view('/slo/post<hoge:re:.*>', SLOController, 'post'),
                view('/slo/redirect<hoge:re:.*>', SLOController, 'redirect')
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

