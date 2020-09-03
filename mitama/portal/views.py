from mitama.http import Response, get_session
from mitama.app import Template, PackageLoader, Environment
from mitama.auth import password_auth, get_jwt, AuthorizationError

env = Environment(loader = PackageLoader(__package__, './templates'))

async def home(request):
    template = env.get_template('home.html')
    return Response.render(template)

async def login(request):
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
            sess['jwt_token'] = get_jwt(result).decode()
            redirect_to = request.query.get('redirect_to', '')
            return Response(
                headers={
                    'Location': redirect_to
                }
            )
        except AuthorizationError as err:
            data['error'] = 'パスワード、またはログイン名が間違っています'
    template = env.get_template('login.html')
    return Response.render(template, data)

