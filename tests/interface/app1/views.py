from mitama.http import Response
from .model import *

async def home(request):
    some = Some()
    some.create()
    return Response(text = 'new some object '+str(some.id))

async def about(request):
    return Response(text = 'this is about')
