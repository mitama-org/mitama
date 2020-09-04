from mitama.http import get_session, Response
from .model import *

async def home(request):
    print('home')
    sess = await get_session(request)
    if 'count' not in sess:
        sess['count'] = 0
    else:
        sess['count'] += 1
    return Response(text = 'new some object '+str(sess['count']))

async def about(request):
    return Response(text = 'this is about')
