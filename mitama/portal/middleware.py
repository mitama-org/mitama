from mitama.models import User
from mitama.app import Middleware
from mitama.app.http import Response

class InitializeMiddleware(Middleware):
    def process(self, request, handler):
        if User.query.count() == 0:
            return Response.redirect(self.app.convert_url('/setup'))
        else:
            return handler(request)

