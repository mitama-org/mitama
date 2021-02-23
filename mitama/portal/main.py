import os
from pathlib import Path

from mitama.app import App as BaseApp
from mitama.app import Router
from mitama.app.method import view, post
from mitama.models import Permission, InnerPermission
from mitama.utils.controllers import static_files, mitama_favicon
from mitama.utils.middlewares import SessionMiddleware, CsrfMiddleware

from .controller import (
    HomeController,
    UsersController,
    GroupsController,
    RegisterController,
    SessionController,
    SLOController,
    ACSController,
    AppsController,
)
from .middleware import InitializeMiddleware

with open(Path(os.path.dirname(__file__)) / "static/icon.png", "rb") as f:
    icon = f.read()


class App(BaseApp):
    name = "Mitama Portal"
    description = "Mitamaのアプリポータルです。他のアプリを確認できる他、配信の設定やグループの編集、ユーザーの招待ができます。"
    icon = icon

    @property
    def view(self):
        view = super().view
        view.globals.update(
            permission=Permission.is_accepted,
            inner_permission=InnerPermission.is_accepted,
        )
        return view

    @property
    def router(self):
        return Router(
            [
                view("/static/<path:path>", static_files()),
                view("/favicon.ico", mitama_favicon()),
                Router(
                    [
                        view("/setup", RegisterController, "setup"),
                        view("/signup", RegisterController, "signup"),
                        view("/login", SessionController, "login"),
                        Router(
                            [
                                view("/", HomeController),
                                view("/settings", HomeController, "settings"),
                                view("/logout", SessionController, "logout"),
                                view("/users", UsersController, "list"),
                                view("/users/invite", UsersController, "create"),
                                view("/users/invite/<id>/delete", UsersController, "cancel"),
                                view("/users/<id>", UsersController, "retrieve"),
                                view("/users/<id>/settings", UsersController, "update"),
                                view("/users/<id>/delete", UsersController, "delete"),
                                view("/groups", GroupsController, "list"),
                                view("/groups/create", GroupsController, "create"),
                                view("/groups/<id>", GroupsController, "retrieve"),
                                post("/groups/<id>/append", GroupsController, "append"),
                                view("/groups/<id>/groups/<gid>/remove", GroupsController, "remove_group"),
                                view("/groups/<id>/users/<uid>/remove", GroupsController, "remove_user"),
                                view(
                                    "/groups/<id>/users/<uid>/accept",
                                    GroupsController,
                                    "accept",
                                ),
                                view(
                                    "/groups/<id>/users/<uid>/forbit",
                                    GroupsController,
                                    "forbit",
                                ),
                                view("/groups/<id>/settings", GroupsController, "update"),
                                view("/groups/<id>/delete", GroupsController, "delete"),
                                view("/apps", AppsController, "list"),
                                view("/apps/settings", AppsController, "update"),
                                view("/acs/post<hoge:re:.*>", ACSController, "post"),
                                view("/acs/redirect<hoge:re:.*>", ACSController, "redirect"),
                                view("/slo/post<hoge:re:.*>", SLOController, "post"),
                                view("/slo/redirect<hoge:re:.*>", SLOController, "redirect"),
                            ],
                            middlewares=[InitializeMiddleware, SessionMiddleware],
                        ),
                    ],
                    middlewares=[CsrfMiddleware]
                )
            ]
        )
