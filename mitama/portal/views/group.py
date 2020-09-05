from . import *
from mitama.nodes import User, Group

async def list(request):
    template = env.get_template('group/list.html')
    return Response.render()

async def create(request):
    template = env.get_template('group/create.html')
    return Response.render()

async def update(request):
    template = env.get_template('group/update.html')
    return Response.render()

async def retrieve(request):
    template = env.get_template('group/retrieve.html')
    return Response.render()

async def delete(request):
    template = env.get_template('group/delete.html')
    return Response.render()


