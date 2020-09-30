from mitama.http import Response
#from mitama.auth import AuthorizationError
from mitama.nodes import User
from mitama.app import Middleware

'''
class SessionMiddleware(Middleware):
    async def process(self, request, handler):
        try:
            request.user = await get_login_state(request)
        except AuthorizationError:
            return Response.redirect(self.app.convert_url('/login?redirect_to='+urllib.parse.quote(str(request.url), safe='')))
        return await handler(request)
'''

class InitializeMiddleware(Middleware):
    async def process(self, request, handler):
        if User.query.count() == 0:
            return Response.redirect(self.app.convert_url('/setup'))
        else:
            return await handler(request)

