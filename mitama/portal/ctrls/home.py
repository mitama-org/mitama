from mitama.app import BaseController
from mitama.http import Response

class HomeController(BaseController):
    async def handler(self, req):
        template = self.view.get_template('home.html')
        return Response.render(template)
