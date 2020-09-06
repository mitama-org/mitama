from . import Metadata, urls
from mitama.app import App
from mitama.http import middleware, get_session
from mitama.auth import check_jwt, AuthorizationError
import urllib

meta = Metadata()
app = App(meta)

@middleware
async def initialize_middleware(request, handler):
    if User.query.count() == 0:
        from .views import setup
        return await setup(request)
    else:
        return await handler(request)

@middleware
async def session_middleware(request, handler):
    try:
        user = get_login_state(request)
    except AuthorizationError:
        return Response(headers = {
            'Location': app.convert_uri('/login?'+urllib.parse.quote(request.uri))
        })
    return await handler(request)

app.router.add_routes(urls.urls)
