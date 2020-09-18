from mitama.app import Controller
from mitama.http import Response
from mitama.nodes import User, Group
from mitama.auth import password_hash, password_auth, get_jwt
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
                print(err)
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
                user.icon = bytearray(data["icon"])
                user.create()
                sess["jwt_token"] = get_jwt(user)
                return Response.redirect(
                    self.app.convert_uri("/")
                )
            except Exception as err:
                print(err)
                error = str(err)
                return await Response.render(template, request, {
                    'error': error
                })
        return await Response.render(template, request)

class HomeController(Controller):
    async def handle(self, request):
        template = self.view.get_template('home.html')
        return await Response.render(template, request)

class UsersController(Controller):
    async def create(self, req):
        return Response()
    async def retrieve(self, req):
        return Response()
    async def update(self, req):
        return Response()
    async def delete(self, req):
        return Response()
    async def list(self, req):
        return Response()

class GroupsController(Controller):
    async def create(self, req):
        return Response()
    async def retrieve(self, req):
        return Response()
    async def update(self, req):
        return Response()
    async def delete(self, req):
        return Response()
    async def list(self, req):
        return Response()
