from mitama.http import Response
from mitama.app import Template, PackageLoader, Environment

env = Environment(loader = PackageLoader(__package__, './templates'))

async def welcome(request):
    template = env.get_template('welcome.html')
    return Response.render(template)
