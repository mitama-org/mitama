from mitama.http import Response
from mitama.auth import AuthorizationError, check_jwt
#from mitama.nodes import User
from mitama.app import Middleware
import urllib

class SessionMiddleware(Middleware):
    async def process(self, request, handler):
        sess = await request.session()
        if 'jwt_token' in sess:
            request.user = check_jwt(sess['jwt_token'])
        else:
            return Response.redirect('/login?redirect_to='+urllib.parse.quote(str(request.url), safe=''))
        return await handler(request)

'''
class InitializeMiddleware(Middleware):
    async def process(self, request, handler):
        if User.query.count() == 0:
            return Response.redirect('/setup')
        else:
            return await handler(request)
'''

