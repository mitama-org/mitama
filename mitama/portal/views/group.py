from . import *
from mitama.nodes import User, Group

async def list(request):
    template = env.get_template('group/list.html')
    return Response.render()

async def create(request):
    template = env.get_template('group/create.html')
    return Response.render(template)

async def update(request):
    id = request.match_info['id']
    group = Group.retrieve(id)
    if request.method == 'POST':
        name = group.get('')
        screen_name = group.get('')
    template = env.get_template('group/update.html')
    return Response.render(template, {
        'group': group
    })

async def retrieve(request):
    id = request.match_info['id']
    group = Group.retrieve(id)
    template = env.get_template('group/retrieve.html')
    return Response.render(template, {
        'group': group
    })

async def delete(request):
    id = request.match_info['id']
    group = Group.retrieve(id)
    template = env.get_template('group/delete.html')
    return Response.render(template, {
        'group': group
    })


