from mitama.app import Controller, AppRegistry
from mitama.http import Response
from mitama.nodes import User, Group
from mitama.auth import password_hash, password_auth, get_jwt, AuthorizationError
from mitama.noimage import load_noimage_group, load_noimage_user
import json
import traceback
from uuid import uuid4
from .model import Invite, CreateUserPermission, UpdateUserPermission, DeleteUserPermission, CreateGroupPermission, UpdateGroupPermission, DeleteGroupPermission, Admin

class SessionController(Controller):
    def login(self, request):
        template = self.view.get_template('login.html')
        if request.method == 'POST':
            try:
                post = request.post()
                result = password_auth(post['screen_name'], post['password'])
                sess = request.session()
                sess['jwt_token'] = get_jwt(result)
                redirect_to = request.query.get('redirect_to', '/')
                return Response.redirect(
                    redirect_to
                )
            except AuthorizationError as err:
                error = 'パスワード、またはログイン名が間違っています'
                return Response.render(
                    template,
                    {
                        'error':error
                    },
                    status = 401
                )
        return Response.render(
            template,
            status = 401
        )

    def logout(self, request):
        sess = request.session()
        sess['jwt_token'] = None
        redirect_to = request.query.get('redirect_to', '/')
        return Response.redirect(redirect_to)

class RegisterController(Controller):
    def signup(self, request):
        sess = request.session()
        template = self.view.get_template('signup.html')
        invite = Invite.query.filter(Invite.token == request.query["token"]).first()
        if request.method == "POST":
            try:
                data = request.post()
                user = User()
                user.password = password_hash(data['password'])
                if invite.editable:
                    user.screen_name = data.get('screen_name', '')
                    user.name = data.get('name', '')
                    user.icon = data['icon'].file.read() if "icon" in data else invite.icon
                else:
                    user.screen_name = invite.screen_name
                    user.name = invite.name
                    user.icon = invite.icon
                user.create()
                invite.delete()
                UpdateUserPermission.accept(user, user)
                sess["jwt_token"] = get_jwt(user)
                return Response.redirect(
                    self.app.convert_url('/')
                )
            except Exception as err:
                error = str(err)
                return Response.render(template, {
                    'error': error,
                    "name": data.get("name", invite.name),
                    "screen_name": data.get("screen_name", invite.screen_name),
                    "password": data.get("password", ''),
                    "icon": data.get("icon").file.read(),
                    'editable': invite.editable
                })
        return Response.render(template, {
            "icon": invite.icon,
            "name": invite.name,
            "screen_name": invite.screen_name,
            'editable': invite.editable
        })
    def setup(self, request):
        sess = request.session()
        template = self.app.view.get_template('setup.html')
        if request.method == 'POST':
            try:
                data = request.post()
                user = User()
                user.screen_name = data['screen_name']
                user.name = data['name']
                user.password = password_hash(data['password'])
                user.icon = data["icon"].file.read() if 'icon' in data else load_noimage_user()
                user.create()
                Admin.accept(user)
                CreateUserPermission.accept(user)
                UpdateUserPermission.accept(user)
                DeleteUserPermission.accept(user)
                CreateGroupPermission.accept(user)
                UpdateGroupPermission.accept(user)
                DeleteGroupPermission.accept(user)
                UpdateUserPermission.accept(user, user)
                sess["jwt_token"] = get_jwt(user)
                return Response.redirect(
                    self.app.convert_url("/")
                )
            except Exception as err:
                error = str(err)
                return Response.render(template, {
                    'error': error
                })
        return Response.render(template)
# HomeControllerではユーザー定義のダッシュボード的なのを作れるようにしたいけど、時間的にパス
'''
class HomeController(Controller):
    def handle(self, request):
        template = self.view.get_template('home.html')
        return Response.render(template)
'''

class UsersController(Controller):
    def create(self, req):
        if CreateUserPermission.is_forbidden(req.user):
            return self.app.error(req, 403)
        template = self.view.get_template('user/create.html')
        invites = Invite.list()
        if req.method == 'POST':
            post = req.post()
            try:
                icon = post["icon"].file.read() if "icon" in post else load_noimage_user()
                invite = Invite()
                invite.name = post.get('name', '')
                invite.screen_name = post.get('screen_name', '')
                invite.icon = icon
                invite.token = str(uuid4())
                invite.editable = 'editable' in post
                invite.create()
                invites = Invite.list()
                return Response.render(template, {
                    'invites': invites,
                    "icon": load_noimage_user()
                })
            except Exception as err:
                error = str(err)
                return Response.render(template, {
                    'invites': invites,
                    "name": post.get("name", ''),
                    "screen_name": post.get("screen_name", ''),
                    "icon": icon,
                    'error': error
                })
        return Response.render(template, {
            'invites': invites,
            "icon": load_noimage_user()
        })
    def cancel(self, req):
        if CreateUserPermission.is_forbidden(req.user):
            return self.app.error(req, 403)
        invite = Invite.retrieve(req.params['id'])
        invite.delete()
        return Response.redirect(self.app.convert_url('/users/invite'))
    def retrieve(self, req):
        template = self.view.get_template('user/retrieve.html')
        user = User.retrieve(screen_name = req.params["id"])
        return Response.render(template, {
            "user": user,
            'updatable': UpdateUserPermission.is_accepted(req.user, user)
        })
    def update(self, req):
        template = self.view.get_template('user/update.html')
        user = User.retrieve(screen_name = req.params["id"])
        if UpdateUserPermission.is_forbidden(req.user, user):
            return self.app.error(req, 403)
        if req.method == "POST":
            post = req.post()
            try:
                icon = post["icon"].file.read() if "icon" in post else user.icon
                user.screen_name = post["screen_name"]
                user.name = post["name"]
                user.icon = icon
                user.update()
                if Admin.is_accepted(req.user):
                    if 'user_create' in post:
                        CreateUserPermission.accept(user)
                    else:
                        CreateUserPermission.forbit(user)
                    if 'user_update' in post:
                        UpdateUserPermission.accept(user)
                    else:
                        UpdateUserPermission.forbit(user)
                    if 'user_delete' in post:
                        DeleteUserPermission.accept(user)
                    else:
                        DeleteUserPermission.forbit(user)
                    if 'group_create' in post:
                        CreateGroupPermission.accept(user)
                    else:
                        CreateGroupPermission.forbit(user)
                    if 'group_update' in post:
                        UpdateGroupPermission.accept(user)
                    else:
                        UpdateGroupPermission.forbit(user)
                    if 'group_delete' in post:
                        DeleteGroupPermission.accept(user)
                    else:
                        DeleteGroupPermission.forbit(user)
                    if 'admin' in post:
                        Admin.accept(user)
                    else:
                        Admin.forbit(user)
                return Response.render(template, {
                    "message": "変更を保存しました",
                    "user": user,
                    "screen_name": user.screen_name,
                    "name": user.name,
                    "icon": user.icon,
                })
            except Exception as err:
                error = str(err)
                return Response.render(template, {
                    "error": error,
                    "user": user,
                    "screen_name": post.get("screen_name", user.screen_name),
                    "name": post.get("name", user.name),
                    "icon": icon,
                })
        return Response.render(template, {
            "user": user,
            "screen_name": user.screen_name,
            "name": user.name,
            "icon": user.icon,
        })
    def delete(self, req):
        if DeleteUserPermission.is_forbidden(req.user):
            return self.app.error(req, 403)
        template = self.view.get_template('user/delete.html')
        return Response.render(template)
    def list(self, req):
        template = self.view.get_template('user/list.html')
        users = User.list()
        return Response.render(template, {
            'users': users,
            'create_permission': CreateUserPermission.is_accepted(req.user),
        })

class GroupsController(Controller):
    def create(self, req):
        if CreateGroupPermission.is_forbidden(req.user):
            return self.app.error(request, 403)
        template = self.view.get_template('group/create.html')
        groups = Group.list()
        if req.method == 'POST':
            post = req.post()
            try:
                group = Group()
                group.name = post['name']
                group.screen_name = post['screen_name']
                group.icon = post['icon'].file.read() if "icon" in post else None
                group.create()
                if "parent" in post and post['parent'] != '':
                    Group.retrieve(int(post['parent'])).append(group)
                group.append(req.user)
                UpdateGroupPermission.accept(req.user, group)
                return Response.redirect(self.app.convert_url("/groups"))
            except Exception as err:
                error = str(err)
                return Response.render(template, {
                    'groups': groups,
                    "icon": load_noimage_group(),
                    'error': error
                })
        return Response.render(template, {
            'groups': groups,
            "icon": load_noimage_group()
        })
    def retrieve(self, req):
        template = self.view.get_template('group/retrieve.html')
        group = Group.retrieve(screen_name = req.params["id"])
        return Response.render(template, {
            "group": group,
            'updatable': UpdateGroupPermission.is_accepted(req.user, group)
        })
    def update(self, req):
        template = self.view.get_template('group/update.html')
        group = Group.retrieve(screen_name = req.params["id"])
        groups = list()
        for g in Group.list():
            if not (group.is_ancestor(g) or group.is_descendant(g) or g==group):
                groups.append(g)
        users = list()
        for u in User.list():
            if not group.is_in(u):
                users.append(u)
        if UpdateGroupPermission.is_forbidden(req.user, group):
            return self.app.error(req, 403)
        if req.method == "POST":
            post = req.post()
            try:
                icon = post["icon"].file.read() if "icon" in post else group.icon
                group.screen_name = post["screen_name"]
                group.name = post["name"]
                group.icon = icon
                group.update()
                if Admin.is_accepted(req.user):
                    if 'user_create' in post:
                        CreateUserPermission.accept(group)
                    else:
                        CreateUserPermission.forbit(group)
                    if 'user_update' in post:
                        UpdateUserPermission.accept(group)
                    else:
                        UpdateUserPermission.forbit(group)
                    if 'user_delete' in post:
                        DeleteUserPermission.accept(group)
                    else:
                        DeleteUserPermission.forbit(group)
                    if 'group_create' in post:
                        CreateGroupPermission.accept(group)
                    else:
                        CreateGroupPermission.forbit(group)
                    if 'group_update' in post:
                        UpdateGroupPermission.accept(group)
                    else:
                        UpdateGroupPermission.forbit(group)
                    if 'group_delete' in post:
                        DeleteGroupPermission.accept(group)
                    else:
                        DeleteGroupPermission.forbit(group)
                    if 'admin' in post:
                        Admin.accept(group)
                    else:
                        Admin.forbit(group)
                return Response.render(template, {
                    "message": "変更を保存しました",
                    "group": group,
                    "screen_name": group.screen_name,
                    "name": group.name,
                    'all_groups': groups,
                    'all_users': users,
                    "icon": group.icon,
                })
            except Exception as err:
                error = str(err)
                return Response.render(template, {
                    "error": error,
                    'all_groups': groups,
                    'all_users': users,
                    "group": group,
                    "screen_name": post.get("screen_name", ''),
                    "name": post.get("name", ''),
                    "icon": group.icon,
                })
        return Response.render(template, {
            "group": group,
            'all_groups': groups,
            'all_users': users,
            "screen_name": group.screen_name,
            "name": group.name,
            "icon": group.icon,
        })
    def append(self, req):
        post = req.post()
        try:
            group = Group.retrieve(screen_name = req.params['id'])
            nodes = list()
            if 'user' in post:
                for uid in post.getlist('user'):
                    try:
                        nodes.append(User.retrieve(int(uid)))
                    except Exception as err:
                        print(err)
                        pass
            if 'group' in post:
                for gid in post.getlist('group'):
                    try:
                        nodes.append(Group.retrieve(int(gid)))
                    except Exception as err:
                        print(err)
                        pass
            group.append_all(nodes)
        except Exception as err:
            pass
        finally:
            return Response.redirect(self.app.convert_url('/groups/'+group.screen_name+'/settings'))
    def remove(self, req):
        try:
            group = Group.retrieve(screen_name = req.params['id'])
            cid = int(req.params['cid'])
            if cid % 2 == 0:
                child = Group.retrieve(cid / 2)
            else:
                child = User.retrieve((cid + 1) / 2)
            group.remove(child)
        except Exception as err:
            pass
        finally:
            return Response.redirect(self.app.convert_url('/groups/'+group.screen_name+'/settings'))
    def accept(self, req):
        group = Group.retrieve(screen_name = req.params['id'])
        if UpdateGroupPermission.is_forbidden(req.user, group):
            return self.app.error(req, 403)
        user = User.retrieve(int(req.params['cid']))
        UpdateGroupPermission.accept(user, group)
        return Response.redirect(self.app.convert_url('/groups/'+group.screen_name+'/settings'))
    def forbit(self, req):
        group = Group.retrieve(screen_name = req.params['id'])
        if UpdateGroupPermission.is_forbidden(req.user, group):
            return self.app.error(req, 403)
        user = User.retrieve(int(req.params['cid']))
        UpdateGroupPermission.forbit(user, group)
        return Response.redirect(self.app.convert_url('/groups/'+group.screen_name+'/settings'))
    def delete(self, req):
        if DeleteGroupPermission.is_forbidden(req.user):
            return self.app.error(req, 403)
        template = self.view.get_template('group/delete.html')
        return Response.render(template)
    def list(self, req):
        template = self.view.get_template('group/list.html')
        groups = Group.tree()
        return Response.render(template, {
            'groups': groups,
            'create_permission': CreateGroupPermission.is_accepted(req.user),
        })

class AppsController(Controller):
    def update(self, req):
        if Admin.is_forbidden(req.user):
            return self.app.error(req, 403)
        template = self.view.get_template('apps/update.html')
        apps = AppRegistry()
        if req.method == "POST":
            apps.reset()
            post = req.post()
            try:
                prefix = post["prefix"]
                data = dict()
                data["apps"] = dict()
                for package, path in prefix.items():
                    data["apps"][package] = {
                        "path": path
                    }
                with open(self.app.project_root_dir / "mitama.json", 'w') as f:
                    f.write(json.dumps(data))
                apps.load_config()
                return Response.render(template, {
                    'message': '変更を保存しました',
                    "apps": apps,
                })
            except Exception as err:
                return Response.render(template, {
                    "apps": apps,
                    'error': str(err)
                })
        return Response.render(template, {
            "apps": apps
        })
    def list(self, req):
        template = self.view.get_template('apps/list.html')
        apps = AppRegistry()
        return Response.render(template, {
            "apps": apps,
        })
