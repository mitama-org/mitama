from mitama.http.server import Response
async def home(request):
    return Response(text = 'this is home')

async def about(request):
    return Response(text = 'this is about')

urls = [
    ('/', home),
    ('/about', about)
]