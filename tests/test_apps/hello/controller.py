from mitama.app import Controller
from mitama.app.http import Response
from mitama.models import Role, User

from .model import Permission

class WelcomeController(Controller):
    def handle(self, request):
        template = self.view.get_template("welcome.html")
        return Response.render(template, {
            "users": User.list()
        })
    def sock(self, request):
        ws = request.websocket
        while True:
            msg = ws.receive()
            print(msg)
            try:
                ws.send(msg)
            except:
                ws.close()
                break
        return Response()
