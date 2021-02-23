import os
from mimetypes import add_type, guess_type
from pathlib import Path

import magic
from jinja2 import *

from mitama.app import Controller
from mitama.app.http import Request, Response
from mitama.models import Group, User

add_type("application/json", ".map")


def static_files(*paths):
    paths_ = list(paths)

    class StaticFileController(Controller):
        """静的ファイルを配信するController

        デフォルトではアプリのパッケージ内の :file:`static/` の中身を配信する。
        """

        paths = paths_

        def __init__(self, app):
            super().__init__(app)
            app_mod_dir = Path(os.path.dirname(__file__))
            self.view = Environment(
                loader=FileSystemLoader(
                    [app_mod_dir / "templates", app_mod_dir / "../app/templates"]
                )
            )
            if len(self.paths) == 0:
                self.paths.append(self.app.install_dir / "static")

        def handle(self, req: Request):
            for path in self.paths:
                filename = path / req.params["path"]
                if filename.is_file():
                    mime = guess_type(str(filename)) or ("application/octet-stream",)
                    with open(filename, "rb") as f:
                        return Response(body=f.read(), content_type=mime[0])
            for path in self.paths:
                filename = path / "404.html"
                if filename.is_file():
                    with open(filename) as f:
                        return Response(
                            text=f.read(),
                            status=404,
                            headers={"content-type": "text/html"},
                        )
            template = self.view.get_template("404.html")
            return Response.render(template, status=404)

    return StaticFileController


def mitama_favicon(*paths):
    paths_ = list(paths)

    class FaviconController(Controller):
        """静的ファイルを配信するController

        デフォルトではアプリのパッケージ内の :file:`static/` の中身を配信する。
        """

        paths = paths_

        def __init__(self, app):
            super().__init__(app)
            app_mod_dir = Path(os.path.dirname(__file__))
            self.view = Environment(
                loader=FileSystemLoader(
                    [app_mod_dir / "templates", app_mod_dir / "../app/templates"]
                )
            )
            if len(self.paths) == 0:
                self.paths.append(app_mod_dir / "../app/static")

        def handle(self, req: Request):
            for path in self.paths:
                filename = path / "favicon.ico"
                if filename.is_file():
                    mime = guess_type(str(filename)) or ("application/octet-stream",)
                    with open(filename, "rb") as f:
                        return Response(body=f.read(), content_type=mime[0])
            for path in self.paths:
                filename = path / "404.html"
                if filename.is_file():
                    with open(filename) as f:
                        return Response(
                            text=f.read(),
                            status=404,
                            headers={"content-type": "text/html"},
                        )
            template = self.view.get_template("404.html")
            return Response.render(template, status=404)

    return FaviconController


class UserCRUDController(Controller):
    def create(self, request):
        post = request.post()
        try:
            user = User()
            user.screen_name = post["screen_name"]
            user.name = post["name"]
            user.set_password(post["password"])
            user.create()
            return Response.json(user.to_dict())
        except KeyError as err:
            error = err
            return Response.json(
                {
                    "error": err.__class__.__name__,
                    "message": err.message,
                    "args": err.args,
                }
            )

    def retrieve(self, request):
        try:
            id = request.params["id"]
            if id.isdigit():
                user = User.retrieve(int(id))
            else:
                user = User.retrieve(screen_name=id)
            return Response.json(user.to_dict())
        except KeyError as err:
            error = err
            return Response.json(
                {
                    "error": err.__class__.__name__,
                    "message": err.message,
                    "args": err.args,
                }
            )

    def icon(self, request):
        try:
            id = request.params["id"]
            if id.isdigit():
                user = User.retrieve(int(id))
            else:
                user = User.retrieve(screen_name=id)
            f = magic.Magic(mime=True, uncompress=True)
            mime = f.from_buffer(group.icon)
            return Response(body=user.icon, content_type=mime)
        except KeyError as err:
            return Response.error(
                {
                    "error": err.__class__.__name__,
                    "message": err.message,
                    "args": err.args,
                }
            )

    def update(self, request):
        try:
            post = request.post()
            id = request.params["id"]
            if id.isdigit():
                user = User.retrieve(int(id))
            else:
                user = User.retrieve(screen_name=id)
            if "screen_name" in post:
                user.screen_name = post["screen_name"]
            if "name" in post:
                user.name = post["name"]
            if "password" in post:
                user.set_password(post["password"])
            user.update()
            return Response.json(user.to_dict())
        except KeyError as err:
            error = err
            return Response.json(
                {
                    "error": err.__class__.__name__,
                    "message": err.message,
                    "args": err.args,
                }
            )

    def delete(self, request):
        try:
            id = request.params["id"]
            if id.isdigit():
                user = User.retrieve(int(id))
            else:
                user = User.retrieve(screen_name=id)
            user.delete()
            return Response.json({"_id": user._id})
        except Exception as err:
            error = err
            return Response.json(
                {
                    "error": err.__class__.__name__,
                    "message": err.message,
                    "args": err.args,
                }
            )

    def list(self, request):
        users = User.list()
        return Response.json([user.to_dict for user in users])


class GroupCRUDController(Controller):
    def create(self, request):
        post = request.post()
        try:
            group = Group()
            group.screen_name = post["screen_name"]
            group.name = post["name"]
            group.create()
            return Response.json(group.to_dict())
        except KeyError as err:
            error = err
            return Response.json(
                {
                    "error": err.__class__.__name__,
                    "message": err.message,
                    "args": err.args,
                }
            )

    def retrieve(self, request):
        try:
            id = request.params["id"]
            if id.isdigit():
                group = Group.retrieve(int(id))
            else:
                group = Group.retrieve(screen_name=id)
            return Response.json(group.to_dict())
        except KeyError as err:
            error = err
            return Response.json(
                {
                    "error": err.__class__.__name__,
                    "message": err.message,
                    "args": err.args,
                }
            )

    def icon(self, request):
        try:
            id = request.params["id"]
            if id.isdigit():
                group = Group.retrieve(int(id))
            else:
                group = Group.retrieve(screen_name=id)
            f = magic.Magic(mime=True, uncompress=True)
            mime = f.from_buffer(group.icon)
            return Response(body=group.icon, content_type=mime)
        except KeyError as err:
            return Response.error(
                {
                    "error": err.__class__.__name__,
                    "message": err.message,
                    "args": err.args,
                }
            )

    def update(self, request):
        try:
            post = request.post()
            id = request.params["id"]
            if id.isdigit():
                group = Group.retrieve(int(id))
            else:
                group = Group.retrieve(screen_name=id)
            if "screen_name" in post:
                group.screen_name = post["screen_name"]
            if "name" in post:
                group.name = post["name"]
            group.update()
            return Response.json(group.to_dict())
        except KeyError as err:
            error = err
            return Response.json(
                {
                    "error": err.__class__.__name__,
                    "message": err.message,
                    "args": err.args,
                }
            )

    def delete(self, request):
        try:
            id = request.params["id"]
            if id.isdigit():
                group = Group.retrieve(int(id))
            else:
                group = Group.retrieve(screen_name=id)
            group.delete()
            return Response.json({"_id": group._id})
        except Exception as err:
            error = err
            return Response.json(
                {
                    "error": err.__class__.__name__,
                    "message": err.message,
                    "args": err.args,
                }
            )

    def list(self, request):
        groups = Group.list()
        return Response.json([group.to_dict() for group in groups])
