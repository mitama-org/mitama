from mitama.http import Response
from mitama.http.auth import get_login_state
from mitama.auth import AuthorizationError
#from mitama.nodes import User
from mitama.app import Middleware
import urllib

class SessionMiddleware(Middleware):
    async def process(self, request, handler):
        try:
            request.user = await get_login_state(request)
        except AuthorizationError:
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

