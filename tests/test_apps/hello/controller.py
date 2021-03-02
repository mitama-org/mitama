from mitama.app import Controller
from mitama.app.http import Response
from mitama.models import Role, User

from .model import Permission

class WelcomeController(Controller):
    def handle(self, request):
        Permission.accept('test', Role.retrieve(screen_name='owner'))
        template = self.view.get_template("welcome.html")
        return Response.render(template)
