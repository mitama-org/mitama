from mitama.app import Controller, AppRegistry
from mitama.http import Response
from mitama.nodes import User, Group
from mitama.auth import password_hash, password_auth, get_jwt, AuthorizationError
from mitama.app.noimage import noimage_group, noimage_user
import json
from uuid import uuid4
from .model import Invite

class SessionController(Controller):
    async def login(self, request):
        template = self.view.get_template('login.html')
        if request.method == 'POST':
            try:
                post = await request.post()
                result = password_auth(post['screen_name'], post['password'])
                sess = await request.session()
                sess['jwt_token'] = get_jwt(result)
                redirect_to = request.query.get('redirect_to', '/')
                return Response.redirect(
                    redirect_to
                )
            except AuthorizationError as err:
                error = 'パスワード、またはログイン名が間違っています'
                return await Response.render(
                    template,
                    request,
                    {
                        'error':error
                    },
                    status = 401
                )
        return await Response.render(
            template,
            request,
            status = 401
        )

    async def logout(self, request):
        sess = await request.session()
        sess['jwt_token'] = None
        redirect_to = request.query.get('redirect_to', '/')
        return Response.redirect(redirect_to)

class RegisterController(Controller):
    async def signup(self, request):
        sess = await request.session()
        template = self.view.get_template('signup.html')
        invite = Invite.query.filter(Invite.token == request.query["token"]).first()
        if request.method == "POST":
            try:
                data = await request.post()
                user = User()
                user.screen_name = data['screen_name']
                user.name = data['name']
                user.password = password_hash(data['password'])
                user.icon = data['icon'].file.read() if "icon" in data else invite.icon
                user.create()
                sess["jwt_token"] = get_jwt(user)
                return Response.redirect(
                    self.app.convert_url('/')
                )
            except Exception as err:
                error = str(err)
                return await Response.render(template, request, {
                    "entrance": True,
                    'error': error,
                    "name": data["name"],
                    "screen_name": data["screen_name"],
                    "password": data["password"],
                    "icon": data["icon"].file.read()
                })
        return await Response.render(template, request, {
            "entrance": True,
            "icon": invite.icon,
            "name": invite.name,
            "screen_name": invite.screen_name,
        })
    async def setup(self, request):
        sess = await request.session()
        template = self.app.view.get_template('setup.html')
        if request.method == 'POST':
            try:
                data = await request.post()
                user = User()
                user.screen_name = data['screen_name']
                user.name = data['name']
                user.password = password_hash(data['password'])
                user.icon = data["icon"].file.read()
                user.create()
                sess["jwt_token"] = get_jwt(user)
                return Response.redirect(
                    self.app.convert_url("/")
                )
            except Exception as err:
                error = str(err)
                return await Response.render(template, request, {
                    "entrance": True,
                    'error': error
                })
        return await Response.render(template, request, {
            "entrance": True,
        })
# HomeControllerではユーザー定義のダッシュボード的なのを作れるようにしたいけど、時間的にパス
'''
class HomeController(Controller):
    async def handle(self, request):
        template = self.view.get_template('home.html')
        return await Response.render(template, request)
'''

class UsersController(Controller):
    async def create(self, req):
        template = self.view.get_template('user/create.html')
        invites = Invite.list()
        if req.method == 'POST':
            post = await req.post()
            try:
                icon = post["icon"].file.read() if "icon" in post else noimage_user
                invite = Invite()
                invite.name = post['name']
                invite.screen_name = post['screen_name']
                invite.icon = icon
                invite.token = str(uuid4())
                invite.create()
                invites = Invites.list()
                return await Response.render(template, req, {
                    'invites': invites,
                    "icon": noimage_user
                })
            except Exception as err:
                error = str(err)
                return await Response.render(template, req, {
                    'invites': invites,
                    "name": post["name"],
                    "screen_name": post["screen_name"],
                    "icon": icon,
                    'error': error
                })
        return await Response.render(template, req, {
            'invites': invites,
            "icon": noimage_user
        })
    async def cancel(self, req):
        invite = Invite.retrieve(req.params['id'])
        invite.delete()
        return Response.redirect(self.app.convert_url('/users/invite'))
    async def retrieve(self, req):
        template = self.view.get_template('user/retrieve.html')
        user = User.retrieve(screen_name = req.params["id"])
        return await Response.render(template, req, {
            "user": user
        })
    async def update(self, req):
        template = self.view.get_template('user/update.html')
        user = User.retrieve(screen_name = req.params["id"])
        if req.method == "POST":
            post = await req.post()
            try:
                icon = post["icon"].file.read() if "icon" in post else user.icon
                user.screen_name = post["screen_name"]
                user.name = post["name"]
                user.icon = icon
                user.update()
                user = User.retrieve(user.id)
                return await Response.render(template, req, {
                    "message": "変更を保存しました",
                    "user": user,
                    "screen_name": user.screen_name,
                    "name": user.name,
                    "icon": user.icon,
                })
            except Exception as err:
                error = str(err)
                return await Response.render(template, req, {
                    "error": error,
                    "user": user,
                    "screen_name": post["screen_name"],
                    "name": post["name"],
                    "icon": icon,
                })
        return await Response.render(template, req, {
            "user": user,
            "screen_name": user.screen_name,
            "name": user.name,
            "icon": user.icon,
        })
    async def delete(self, req):
        template = self.view.get_template('user/delete.html')
        return await Response.render(template, req)
    async def list(self, req):
        template = self.view.get_template('user/list.html')
        users = User.list()
        return await Response.render(template, req, {
            'users': users
        })

class GroupsController(Controller):
    async def create(self, req):
        template = self.view.get_template('group/create.html')
        groups = Group.list()
        if req.method == 'POST':
            post = await req.post()
            try:
                group = Group()
                group.name = post['name']
                group.screen_name = post['screen_name']
                group.icon = post['icon'].file.read() if "icon" in post else noimage_group
                group.create()
                if "parent" in post:
                    Group.query.filter(Group.id == post['parent']).first().append(group)
                group.append(req.user)
                return Response.redirect(self.app.convert_url("/groups"))
            except Exception as err:
                error = str(err)
                return await Response.render(template, req, {
                    'groups': groups,
                    "icon": post["icon"].file.read() if "icon" in post else noimage_group,
                    'error': error
                })
        return await Response.render(template, req, {
            'groups': groups,
            "icon": noimage_group
        })
    async def retrieve(self, req):
        template = self.view.get_template('group/retrieve.html')
        group = Group.retrieve(screen_name = req.params["id"])
        return await Response.render(template, req, {
            "group": group
        })
    async def update(self, req):
        template = self.view.get_template('group/update.html')
        group = Group.retrieve(screen_name = req.params["id"])
        if req.method == "POST":
            post = await req.post()
            try:
                icon = post["icon"].file.read() if "icon" in post else group.icon
                group.screen_name = post["screen_name"]
                group.name = post["name"]
                group.icon = icon
                group.update()
                group = group.retrieve(group.id)
                return await Response.render(template, req, {
                    "message": "変更を保存しました",
                    "group": group,
                    "screen_name": group.screen_name,
                    "name": group.name,
                    "icon": group.icon,
                })
            except Exception as err:
                error = str(err)
                return await Response.render(template, req, {
                    "error": error,
                    "group": group,
                    "screen_name": post["screen_name"],
                    "name": post["name"],
                    "icon": icon,
                })
        return await Response.render(template, req, {
            "group": group,
            "screen_name": group.screen_name,
            "name": group.name,
            "icon": group.icon,
        })
    async def delete(self, req):
        template = self.view.get_template('group/delete.html')
        return await Response.render(template, req)
    async def list(self, req):
        template = self.view.get_template('group/list.html')
        groups = Group.tree()
        return await Response.render(template, req, {
            'groups': groups
        })

class AppsController(Controller):
    async def update(self, req):
        template = self.view.get_template('apps/update.html')
        apps = AppRegistry()
        apps.reset()
        if req.method == "POST":
            post = await req.post()
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
                return await Response.render(template, req, {
                    'message': '変更を保存しました',
                    "apps": apps,
                })
            except Exception as err:
                return await Response.render(template, req, {
                    "apps": apps,
                    'error': str(err)
                })
        return await Response.render(template, req, {
            "apps": apps
        })
    async def list(self, req):
        template = self.view.get_template('apps/list.html')
        apps = AppRegistry()
        return await Response.render(template, req, {
            "apps": apps
        })
