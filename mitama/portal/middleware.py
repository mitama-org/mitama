from mitama.http import Response
from mitama.nodes import User
from mitama.app import Middleware

class InitializeMiddleware(Middleware):
    def process(self, request, handler):
        if User.query.count() == 0:
            return Response.redirect(self.app.convert_url('/setup'))
        else:
            return handler(request)

