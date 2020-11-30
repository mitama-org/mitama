from mitama.app import Controller
from mitama.app.http import Response


class WelcomeController(Controller):
    def handle(self, request):
        template = self.view.get_template("welcome.html")
        return Response.render(template)
