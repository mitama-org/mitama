from mitama.app import Controller
from mitama.app.http import Response


class HomeController(Controller):
    def handle(self, request):
        template = self.view.get_template("home.html")
        return Response.render(template)
