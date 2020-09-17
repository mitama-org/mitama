from mitama.app import Controller
from mitama.http import Response, get_session

class SessionController(Controller):
    async def login(self, req):
        data = {}
        if request.method == 'POST':
            post = await request.post()
            screen_name = post.get('screen_name', '')
            password = post.get('password', '')
            data['screen_name'] = screen_name
            data['password'] = password
            try:
                result = password_auth(screen_name, password)
                sess = await get_session(request)
                sess['jwt_token'] = get_jwt(result)
                redirect_to = request.query.get('redirect_to', '')
                return Response(
                    headers={
                        'Location': redirect_to
                    },
                    status = 200
                )
            except AuthorizationError as err:
                data['error'] = 'パスワード、またはログイン名が間違っています'
        template = env.get_template('login.html')
        return Response.render(
            template,
            data,
            status = 401
        )
    async def logout(self, req):
        sess = await get_session()
        sess['jwt_token'] = None
        return Response.redirect(
            self.app.convert_uri('/')
        )
