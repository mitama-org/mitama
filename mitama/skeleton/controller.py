from mitama.app import Controller
from mitama.http import Response

class WelcomeController(Controller):
    async def handle(self, request):
        template = self.view.get_template('welcome.html')
        return await Response.render(template, request)
