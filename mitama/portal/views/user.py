from . import *
from mitama.nodes import User

async def list(request):
    template = env.get_template('user/list.html')
    return Response.render()

async def create(request):
    template = env.get_template('user/create.html')
    return Response.render()

async def update(request):
    template = env.get_template('user/update.html')
    return Response.render()

async def retrieve(request):
    template = env.get_template('user/retrieve.html')
    return Response.render()

async def delete(request):
    template = env.get_template('user/delete.html')
    return Response.render()


