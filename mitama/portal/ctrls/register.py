from mitama.app import Controller
from mitama.http import Response

class RegisterController(Controller):
    async def signup(request):
        sess = await get_session()
        if request.method == "POST":
            post = await request.post()
            icon = post["icon"]
            screen_name = post["screen_name"]
            name = post["name"]
            password = post["password"]
            data["screen_name"] = screen_name
            data["name"] = name
            try:
                user = User()
                user.screen_name = screen_name
                user.name = name
                user.password = password_hash(password)
                user.create()
                sess["jwt_token"] = get_jwt(user)
                return Response.redirect(
                    self.convert_uri('/')
                )
            except Exception as err:
                data["error"] = str(err)
        template = self.view.get_template('signup.html')
        return Response.render(template, data)
    async def setup(request):
        sess = await get_session()
        if request.method == "POST":
            post = await request.post()
            icon = post["icon"]
            screen_name = post["screen_name"]
            name = post["name"]
            password = post["password"]
            data["screen_name"] = screen_name
            data["name"] = name
            try:
                user = User()
                user.screen_name = screen_name
                user.name = name
                user.password = password_hash(password)
                user.create()
                sess["jwt_token"] = get_jwt(user)
                return Response.redirect(
                    self.convert_uri("/")
                )
            except Exception as err:
                data["error"] = str(err)
        template = self.view.get_template('setup.html')
        return Response.render(template, data)

