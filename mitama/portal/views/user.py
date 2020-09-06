from . import *
from mitama.nodes import User

async def list(request):
    template = env.get_template('user/list.html')
    users = User.query.all()
    return Response.render(template, {
        'users': users
    })

async def create(request):
    template = env.get_template('user/create.html')
    if request.method == 'POST':
        post = await request.post()
    return Response.render()

async def update(request):
    template = env.get_template('user/update.html')
    user = User.retrieve(id)
    if request.method == 'POST':
        post = await request.post()
        name = post.get('name') or user.name
        screen_name = post.get('screen_name') or user.screen_name
        user.name = name
        user.screen_name = screen_name
        user.update()
    return Response.render(template, {
        'user': user
    })

async def retrieve(request):
    template = env.get_template('user/retrieve.html')
    user = User.retrieve(id)
    return Response.render(template, {})

async def delete(request):
    template = env.get_template('user/delete.html')
    user = User.retrieve(id)
    if request.method == 'POST':
        post = await request.post()
    return Response.render(template, {})


