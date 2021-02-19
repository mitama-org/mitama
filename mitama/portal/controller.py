import json
import traceback
from uuid import uuid4

from mitama.app import AppRegistry, Controller
from mitama.app.http import Response
from mitama.models import AuthorizationError, Group, User, Role, Permission
from mitama.app.forms import ValidationError
from mitama.noimage import load_noimage_group, load_noimage_user

from .forms import (
    SetupForm,
    LoginForm,
    RegisterForm,
    InviteForm,
    UserUpdateForm,
    GroupCreateForm,
    GroupUpdateForm,
    AppUpdateForm,
)

class SessionController(Controller):
    def login(self, request):
        template = self.view.get_template("login.html")
        if request.method == "POST":
            try:
                form = LoginForm(request.post())
                result = User.password_auth(
                    form["screen_name"],
                    form["password"]
                )
                sess = request.session()
                sess["jwt_token"] = User.get_jwt(result)
                redirect_to = request.query.get("redirect_to", ["/"])[0]
                return Response.redirect(redirect_to)
            except ValidationError as err:
                return Response.render(template, {"error": err.message}, status=401)
        return Response.render(template, status=401)

    def logout(self, request):
        sess = request.session()
        sess["jwt_token"] = None
        redirect_to = request.query.get("redirect_to", ["/"])[0]
        return Response.redirect(redirect_to)


class RegisterController(Controller):
    def signup(self, request):
        sess = request.session()
        template = self.view.get_template("signup.html")
        user = User.retrieve(_token=request.query["token"][0])
        if request.method == "POST":
            try:
                form = RegisterForm(request.post())
                user.set_password(form["password"])
                user.screen_name = form["screen_name"]
                user.name = form["name"]
                user.icon = form["icon"] or user.icon
                user.update()
                sess["jwt_token"] = User.get_jwt(user)
                return Response.redirect(self.app.convert_url("/"))
            except ValidationError as err:
                icon = form["icon"]
                return Response.render(
                    template,
                    {
                        "error": err.messsage,
                        "name": form["name"] or user.name,
                        "screen_name": form["screen_name"] or user.screen_name,
                        "password": form["password"] or "",
                        "icon": icon,
                    },
                )
        return Response.render(
            template,
            {
                "icon": user.icon,
                "name": user.name or "",
                "screen_name": user.screen_name or "",
            },
        )

    def setup(self, request):
        sess = request.session()
        template = self.view.get_template("setup.html")
        if len(User.list()) > 0:
            return Response.redirect(self.app.convert_url("/login"))
        if request.method == "POST":
            try:
                form = SetupForm(request.post())
                user = User()
                user.email = form["email"]
                user._token = str(uuid4())
                user.create()
                user.mail(
                    "Mitamaへようこそ",
                    "下記リンクから、Mitamaに参加しましょう\n{}".format(self.app.convert_fullurl(request, "/signup?token=" + user._token))
                )

                owner = Role()
                owner.screen_name = "owner"
                owner.name = "Owner"
                owner.create()
                manager = Role()
                manager.screen_name = "manager"
                manager.name = "Manager"
                owner.create()
                normal = Role()
                normal.screen_name = "normal"
                normal.name = "Normal"
                owner.create()

                Permission.accept("admin", owner)
                Permission.accept("create_user", owner)
                Permission.accept("update_user", owner)
                Permission.accept("delete_user", owner)
                Permission.accept("create_group", owner)
                Permission.accept("update_group", owner)
                Permission.accept("delete_group", owner)
                Permission.accept("create_user", manager)
                Permission.accept("update_user", manager)
                Permission.accept("create_group", manager)
                Permission.accept("update_group", manager)

                user.roles.append(owner)
                user.update()

                template = self.view.get_template("confirm.html")
                return Response.render(template)
            except ValidationError as err:
                return Response.render(template, {"error": err.message})
        return Response.render(template)


# HomeControllerではユーザー定義のダッシュボード的なのを作れるようにしたいけど、時間的にパス
"""
class HomeController(Controller):
    def handle(self, request):
        template = self.view.get_template('home.html')
        return Response.render(template)
"""


class UsersController(Controller):
    def create(self, req):
        template = self.view.get_template("user/create.html")
        invites = Invite.list()
        if req.method == "POST":
            form = InviteForm(req.post())
            try:
                user = User()
                user.name = form["name"]
                user.screen_name = form["screen_name"]
                user.icon = form["icon"]
                user.email = form["email"]
                user._token = str(uuid4())
                user.create()
                user.mail(
                    "Mitamaに招待されています",
                    "下記リンクから、Mitamaに参加しましょう\n{}".format(self.convert_fullurl("/signup?token=" + invite.token))
                )
                return Response.render(
                    template, {"invites": invites, "icon": load_noimage_user()}
                )
            except Exception as err:
                error = str(err)
                return Response.render(
                    template,
                    {
                        "invites": invites,
                        "name": form["name"],
                        "screen_name": form["screen_name"],
                        "icon": form["icon"],
                        "error": error,
                    },
                )
        return Response.render(
            template, {"invites": invites, "icon": load_noimage_user()}
        )

    def cancel(self, req):
        invite = Invite.retrieve(req.params["id"])
        invite.delete()
        return Response.redirect(self.app.convert_url("/users/invite"))

    def retrieve(self, req):
        template = self.view.get_template("user/retrieve.html")
        user = User.retrieve(screen_name=req.params["id"])
        return Response.render(
            template,
            {
                "user": user,
            },
        )

    def update(self, req):
        template = self.view.get_template("user/update.html")
        user = User.retrieve(screen_name=req.params["id"])
        roles = Role.list()
        if req.method == "POST":
            form = UserUpdateForm(req.post())
            try:
                user.screen_name = form["screen_name"]
                user.name = form["name"]
                user.icon = form["icon"] or user.icon
                user.update()
                return Response.render(
                    template,
                    {
                        "message": "変更を保存しました",
                        "user": user,
                        "screen_name": user.screen_name,
                        "name": user.name,
                        "icon": user.icon,
                        "roles": roles
                    },
                )
            except ValidationError as err:
                error = err.message
                return Response.render(
                    template,
                    {
                        "error": error,
                        "user": user,
                        "screen_name": form["screen_name"] or user.screen_name,
                        "name": form["name"] or user.name,
                        "icon": form["icon"],
                        "roles": roles
                    },
                )
        return Response.render(
            template,
            {
                "user": user,
                "screen_name": user.screen_name,
                "name": user.name,
                "icon": user.icon,
                "roles": roles
            },
        )

    def delete(self, req):
        template = self.view.get_template("user/delete.html")
        return Response.render(template)

    def list(self, req):
        template = self.view.get_template("user/list.html")
        users = User.list()
        return Response.render(
            template,
            {
                "users": users,
            },
        )


class GroupsController(Controller):
    def create(self, req):
        template = self.view.get_template("group/create.html")
        groups = Group.list()
        if req.method == "POST":
            form = GroupCreateForm(req.post())
            try:
                group = Group()
                group.name = form["name"]
                group.screen_name = form["screen_name"]
                group.icon = form["icon"]
                group.create()
                if "parent" in form and form["parent"] != "":
                    Group.retrieve(form["parent"]).append(group)
                group.append(req.user)
                return Response.redirect(self.app.convert_url("/groups"))
            except ValidationError as err:
                return Response.render(
                    template,
                    {"groups": groups, "icon": load_noimage_group(), "error": err.message},
                )
        return Response.render(
            template, {"groups": groups, "icon": load_noimage_group()}
        )

    def retrieve(self, req):
        template = self.view.get_template("group/retrieve.html")
        group = Group.retrieve(screen_name=req.params["id"])
        return Response.render(
            template,
            {
                "group": group,
            },
        )

    def update(self, req):
        template = self.view.get_template("group/update.html")
        roles = Role.list()
        group = Group.retrieve(screen_name=req.params["id"])
        groups = list()
        for g in Group.list():
            if not (group.is_ancestor(g) or group.is_descendant(g) or g == group):
                groups.append(g)
        users = list()
        for u in User.list():
            if not group.is_in(u):
                users.append(u)
        if req.method == "POST":
            form = GroupUpdateForm(req.post())
            try:
                icon = form["icon"] or group.icon
                group.screen_name = form["screen_name"]
                group.name = form["name"]
                for role in form["roles"]:
                    group.roles.append(Role.retrieve(screen_name=role))
                group.icon = icon
                group.update()
                return Response.render(
                    template,
                    {
                        "message": "変更を保存しました",
                        "group": group,
                        "screen_name": group.screen_name,
                        "name": group.name,
                        "all_groups": groups,
                        "all_users": users,
                        "icon": group.icon,
                        "roles": roles
                    },
                )
            except ValidationError as err:
                error = err.message
                return Response.render(
                    template,
                    {
                        "error": error,
                        "all_groups": groups,
                        "all_users": users,
                        "group": group,
                        "screen_name": form["screen_name"],
                        "name": form["name"],
                        "icon": group.icon,
                        "roles": roles
                    },
                )
        return Response.render(
            template,
            {
                "group": group,
                "all_groups": groups,
                "all_users": users,
                "screen_name": group.screen_name,
                "name": group.name,
                "icon": group.icon,
                "roles": roles
            },
        )

    def append(self, req):
        form = req.post()
        try:
            group = Group.retrieve(screen_name=req.params["id"])
            nodes = list()
            if "user" in form:
                for uid in form.getlist("user"):
                    try:
                        nodes.append(User.retrieve(uid))
                    except Exception as err:
                        pass
            if "group" in form:
                for gid in form.getlist("group"):
                    try:
                        nodes.append(Group.retrieve(gid))
                    except Exception as err:
                        pass
            print(nodes)
            group.append_all(nodes)
        except Exception:
            pass
        finally:
            return Response.redirect(
                self.app.convert_url("/groups/" + group.screen_name + "/settings")
            )

    def remove(self, req):
        try:
            group = Group.retrieve(screen_name=req.params["id"])
            child = User.retrieve(request.params["cid"])
            group.remove(child)
        except Exception:
            pass
        finally:
            return Response.redirect(
                self.app.convert_url("/groups/" + group.screen_name + "/settings")
            )

    def accept(self, req):
        group = Group.retrieve(screen_name=req.params["id"])
        user = User.retrieve(int(req.params["cid"]))
        return Response.redirect(
            self.app.convert_url("/groups/" + group.screen_name + "/settings")
        )

    def forbit(self, req):
        group = Group.retrieve(screen_name=req.params["id"])
        user = User.retrieve(int(req.params["cid"]))
        return Response.redirect(
            self.app.convert_url("/groups/" + group.screen_name + "/settings")
        )

    def delete(self, req):
        template = self.view.get_template("group/delete.html")
        return Response.render(template)

    def list(self, req):
        template = self.view.get_template("group/list.html")
        groups = Group.tree()
        return Response.render(
            template,
            {
                "groups": groups,
            },
        )


class AppsController(Controller):
    def update(self, req):
        if Admin.is_forbidden(req.user):
            return self.app.error(req, 403)
        template = self.view.get_template("apps/update.html")
        apps = AppRegistry()
        if req.method == "POST":
            apps.reset()
            form = AppUpdateForm(req.post())
            try:
                prefix = form["prefix"]
                data = dict()
                data["apps"] = dict()
                for package, path in prefix.items():
                    data["apps"][package] = {"path": path}
                with open(self.app.project_root_dir / "mitama.json", "w") as f:
                    f.write(json.dumps(data))
                apps.load_config()
                return Response.render(
                    template,
                    {
                        "message": "変更を保存しました",
                        "apps": apps,
                    },
                )
            except Exception as err:
                return Response.render(template, {"apps": apps, "error": str(err)})
        return Response.render(template, {"apps": apps})

    def list(self, req):
        template = self.view.get_template("apps/list.html")
        apps = AppRegistry()
        return Response.render(
            template,
            {
                "apps": apps,
            },
        )


class ACSController(Controller):
    def redirect(request):
        pass

    def post(request):
        pass


class SLOController(Controller):
    def redirect(request):
        pass

    def post(request):
        pass
