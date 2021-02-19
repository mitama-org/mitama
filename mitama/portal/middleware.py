from mitama.app import Middleware
from mitama.app.http import Response
from mitama.models import User


class InitializeMiddleware(Middleware):
    def process(self, request, handler):
        if User.query.filter(User.password != None).count() == 0:
            return Response.redirect(self.app.convert_url("/setup"))
        else:
            return handler(request)
