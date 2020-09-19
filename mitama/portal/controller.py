from mitama.app import Controller
from mitama.http import Response
from mitama.nodes import User, Group
from mitama.auth import password_hash, password_auth, get_jwt
from uuid import uuid4
from .model import Invite

class RegisterController(Controller):
    async def signup(request):
        sess = await request.session()
        template = self.view.get_template('signup.html')
        if request.method == "POST":
            try:
                data = await request.post()
                user = User()
                user.screen_name = data['screen_name']
                user.name = data['name']
                user.password = password_hash(data['password'])
                user.icon = data['icon']
                user.create()
                sess["jwt_token"] = get_jwt(user)
                return Response.redirect(
                    self.app.convert_uri('/')
                )
            except Exception as err:
                error = str(err)
                return await Response.render(template, request, {
                    'error': error
                })
        return await Response.render(template, request)
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
                    self.app.convert_uri("/")
                )
            except Exception as err:
                error = str(err)
                return await Response.render(template, request, {
                    'error': error
                })
        return await Response.render(template, request)
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
                invite = Invite()
                invite.name = post['name']
                invite.screen_name = post['screen_name']
                invite.icon = post['icon'].file.read()
                invite.token = str(uuid4())
                invite.create()
            except Exception as err:
                error = str(err)
                return await Response.render(template, req, {
                    'invites': invites,
                    'error': error
                })
        return await Response.render(template, req, {
            'invites': invites
        })
    async def cancel(self, req):
        invite = Invite.retrieve(req.params['id'])
        invite.delete()
        return Response.redirect(self.app.convert_uri('/users/invite'))
    async def retrieve(self, req):
        template = self.view.get_template('user/retrieve.html')
        return await Response.render(template, req)
    async def update(self, req):
        template = self.view.get_template('user/update.html')
        return await Response.render(template, req)
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
        return await Response.render(template, req)
    async def retrieve(self, req):
        template = self.view.get_template('group/retrieve.html')
        return await Response.render(template, req)
    async def update(self, req):
        template = self.view.get_template('group/update.html')
        return await Response.render(template, req)
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
        return await Response.render(template, req)
    async def list(self, req):
        template = self.view.get_template('apps/list.html')
        return await Response.render(template, req)
