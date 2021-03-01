import json
import traceback
import io
from uuid import uuid4

from mitama.app import AppRegistry, Controller
from mitama.app.http import Response
from mitama.models import (
    AuthorizationError,
    Group,
    User,
    Role,
    UserInvite,
    InnerRole,
    Permission,
    InnerPermission,
    UserGroup,
)
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
    SettingsForm
)

from PIL import Image

def resize_icon(icon):
    if icon is None:
        return None
    try:
        img = Image.open(io.BytesIO(icon))
    except Exception:
        return icon
    width, height = img.size
    if width > height:
        scale = 200 / height
    else:
        scale = 200 / width
    width *= scale
    height *= scale
    print(width, height)
    resize = img.resize((int(width), int(height)), resample=Image.NEAREST)
    if width > height:
        cropped = resize.crop((int((width-height)/2), 0, width - int((width-height)/2), height))
    else:
        cropped = resize.crop((0, int((height-width)/2), width, height - int((height-width)/2)))
    print(cropped.size, width, height, int((width-height)/2))
    export = io.BytesIO()
    cropped.save(export, format="PNG")
    return export.getvalue()

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
            except Exception as err:
                return Response.render(template, {"error": err}, status=401)
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
        invite = UserInvite.retrieve(token=request.query["token"][0])
        if request.method == "POST":
            try:
                form = RegisterForm(request.post())
                user = User()
                user.email = invite.email
                user.set_password(form["password"])
                user.screen_name = form["screen_name"]
                user.name = form["name"]
                user.icon = resize_icon(form["icon"]) if form["icon"] is not None else user.icon
                user.create()
                invite.delete()
                for role_screen_name in invite.roles.split(":"):
                    role = Role.retrieve(screen_name = role_screen_name)
                    role.append(user)
                sess["jwt_token"] = User.get_jwt(user)
                return Response.redirect(self.app.convert_url("/"))
            except (ValidationError, ValueError) as err:
                icon = form["icon"]
                return Response.render(
                    template,
                    {
                        "error": err.messsage,
                        "name": form["name"] or invite.name,
                        "screen_name": form["screen_name"] or invite.screen_name,
                        "password": form["password"] or "",
                        "icon": icon,
                    },
                )
        return Response.render(
            template,
            {
                "icon": invite.icon,
                "name": invite.name or "",
                "screen_name": invite.screen_name or "",
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
                user = UserInvite()
                user.email = form["email"]
                user.roles = "owner"
                user.create()
                user.mail(
                    "Mitamaへようこそ",
                    "下記リンクから、Mitamaに参加しましょう\n{}".format(self.app.convert_fullurl(request, "/signup?token=" + user.token))
                )

                try:
                    owner = Role()
                    owner.screen_name = "owner"
                    owner.name = "Owner"
                    owner.create()
                    manager = Role()
                    manager.screen_name = "manager"
                    manager.name = "Manager"
                    manager.create()
                    normal = Role()
                    normal.screen_name = "normal"
                    normal.name = "Normal"
                    normal.create()
                    inner_owner = InnerRole()
                    inner_owner.screen_name = "owner"
                    inner_owner.name = "Owner"
                    inner_owner.create()
                    inner_manager = InnerRole()
                    inner_manager.screen_name = "manager"
                    inner_manager.name = "Manager"
                    inner_manager.create()
                    inner_normal = InnerRole()
                    inner_normal.screen_name = "normal"
                    inner_normal.name = "Normal"
                    inner_normal.create()
                except Exception:
                    pass

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

                InnerPermission.accept("admin", inner_owner)
                InnerPermission.accept("add_user", inner_owner)
                InnerPermission.accept("remove_user", inner_owner)
                InnerPermission.accept("add_group", inner_owner)
                InnerPermission.accept("remove_group", inner_owner)
                InnerPermission.accept("add_user", inner_manager)
                InnerPermission.accept("remove_user", inner_owner)
                InnerPermission.accept("add_group", inner_manager)
                InnerPermission.accept("remove_group", inner_owner)

                template = self.view.get_template("confirm.html")
                return Response.render(template)
            except ValidationError as err:
                return Response.render(template, {"error": str(err)})
        return Response.render(template)


class HomeController(Controller):
    def handle(self, request):
        template = self.view.get_template('home.html')
        try:
            with open(self.app.project_dir / "welcome_message.md", "r") as f:
                welcome_message = f.read()
        except Exception:
            welcome_message = """
# Mitamaへようこそ

このページに社内システムの使い方を記述しておきましょう！
            """
        return Response.render(template, {
            "welcome_message": welcome_message
        })
    def settings(self, request):
        template = self.view.get_template("settings.html")
        try:
            with open(self.app.project_dir / "welcome_message.md", "r") as f:
                welcome_message = f.read()
        except Exception:
            welcome_message = """
# Mitamaへようこそ

このページに社内システムの使い方を記述しておきましょう！
            """
        if request.method == "POST":
            try:
                form = SettingsForm(request.post())
                welcome_message_ = form["welcome_message"]
                if form["role_screen_name"] is not None:
                    role = Role()
                    role.screen_name = form['role_screen_name']
                    role.name = form['role_name'] if form['role_name'] is not None else form['role_screen_name']
                    role.create()
                for role_screen_name, role_permissions in form['role'].items():
                    role = Role.retrieve(screen_name = role_screen_name)
                    role.permissions = [Permission.retrieve(screen_name=permission) for permission in role_permissions]
                    role.update()
                if form["inner_role_screen_name"] is not None:
                    inner_role = InnerRole()
                    inner_role.screen_name = form['inner_role_screen_name']
                    inner_role.name = form['inner_role_name'] if form['inner_role_name'] is not None else form['inner_role_screen_name']
                    inner_role.create()
                for inner_role_screen_name, inner_role_permissions in form['inner_role'].items():
                    inner_role = InnerRole.retrieve(screen_name = inner_role_screen_name)
                    inner_role.permissions = [InnerPermission.retrieve(screen_name=permission) for permission in inner_role_permissions]
                    inner_role.update()
                with open(self.app.project_dir / "welcome_message.md", "w") as f:
                    f.write(welcome_message_)
                error = "変更を保存しました"
            except ValidationError as err:
                error = str(err)
            welcome_message = welcome_message_
            return Response.render(template, {
                "welcome_message": welcome_message,
                'roles': Role.list(),
                'permissions': Permission.list(),
                'inner_roles': InnerRole.list(),
                'inner_permissions': InnerPermission.list(),
                "error": error
            })
        return Response.render(template, {
            "welcome_message": welcome_message,
            'roles': Role.list(),
            'permissions': Permission.list(),
            'inner_roles': InnerRole.list(),
            'inner_permissions': InnerPermission.list(),
        })


class UsersController(Controller):
    def create(self, req):
        template = self.view.get_template("user/create.html")
        invites = User.query.filter(User.password==None).all()
        if req.method == "POST":
            try:
                form = InviteForm(req.post())
                user = UserInvite()
                user.email = form["email"]
                user.name = form["name"]
                user.screen_name = form["screen_name"]
                user._icon = resize_icon(form["icon"])
                user.roles = ":".join(form["roles"])
                user.create()
                user.mail(
                    "Mitamaに招待されています",
                    "下記リンクから、Mitamaに参加しましょう\n{}".format(self.app.convert_fullurl(req, "/signup?token=" + user.token))
                )
                return Response.render(
                    template,
                    {
                        "invites": invites,
                        "roles": Role.list(),
                        "icon": load_noimage_user()
                    }
                )
            except Exception as err:
                error = str(err)
                return Response.render(
                    template,
                    {
                        "invites": invites,
                        "roles": Role.list(),
                        "name": form["name"],
                        "screen_name": form["screen_name"],
                        "icon": resize_icon(form["icon"]),
                        "error": error,
                    },
                )
        return Response.render(
            template,
            {
                "invites": invites,
                "roles": Role.list(),
                "icon": load_noimage_user()
            }
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
                user.icon = resize_icon(form["icon"]) if form["icon"] is not None else user.icon
                for role in form["roles"]:
                    user.roles.append(Role.retrieve(screen_name=role))
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
            except Exception as err:
                error = str(err)
                return Response.render(
                    template,
                    {
                        "error": error,
                        "user": user,
                        "screen_name": form["screen_name"] or user.screen_name,
                        "name": form["name"] or user.name,
                        "icon": resize_icon(form["icon"]),
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
                group.icon = resize_icon(form["icon"])
                group.create()
                if form["parent"] != None:
                    Group.retrieve(form["parent"]).append(group)
                group.append(req.user)
                return Response.redirect(self.app.convert_url("/groups"))
            except ValidationError as err:
                return Response.render(
                    template,
                    {"groups": groups, "icon": load_noimage_group(), "error": str(err)},
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
        inner_roles = InnerRole.list()
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
                icon = resize_icon(form["icon"]) if form["icon"] is not None else group.icon
                group.screen_name = form["screen_name"]
                group.name = form["name"]
                for role in form["roles"]:
                    group.roles.append(Role.retrieve(screen_name=role))
                group.icon = icon
                group.users = [User.retrieve(user) for user in form['users']]
                if form['new_user'] is not None:
                    group.users.append(User.retrieve(form['new_user']))
                for user, roles in form['inner_roles'].items():
                    rel = UserGroup.retrieve(group = group, user = User.retrieve(user))
                    rel.roles = [InnerRole.retrieve(screen_name = role) for role in roles]
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
                        "roles": Role.list(),
                        "inner_roles": inner_roles
                    },
                )
            except ValidationError as err:
                error = str(err)
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
                        "roles": Role.list(),
                        "inner_roles": inner_roles
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
                "roles": roles,
                "inner_roles": inner_roles
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
            group.append_all(nodes)
        except Exception:
            pass
        finally:
            return Response.redirect(
                self.app.convert_url("/groups/" + group.screen_name + "/settings")
            )

    def remove_user(self, req):
        try:
            group = Group.retrieve(screen_name=req.params["id"])
            child = User.retrieve(req.params["uid"])
            group.remove(child)
        except Exception as err:
            print(err)
            pass
        finally:
            return Response.redirect(
                self.app.convert_url("/groups/" + group.screen_name + "/settings")
            )

    def remove_group(self, req):
        try:
            group = Group.retrieve(screen_name=req.params["id"])
            child = Group.retrieve(req.params["gid"])
            group.remove(child)
        except Exception as err:
            print(err)
            pass
        finally:
            return Response.redirect(
                self.app.convert_url("/groups/" + group.screen_name + "/settings")
            )

    def accept(self, req):
        group = Group.retrieve(screen_name=req.params["id"])
        user = User.retrieve(req.params["uid"])
        inner_role = InnerRole.retrieve(screen_name = "admin")
        inner_role.append(group, user)
        return Response.redirect(
            self.app.convert_url("/groups/" + group.screen_name + "/settings")
        )

    def forbit(self, req):
        group = Group.retrieve(screen_name=req.params["id"])
        user = User.retrieve(req.params["uid"])
        inner_role = InnerRole.retrieve(screen_name = "admin")
        inner_role.remove(group, user)
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
