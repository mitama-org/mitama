from . import Metadata, urls
from mitama.app import App
from mitama.http import middleware, get_session, Response
from mitama.http.auth import get_login_state
from mitama.auth import AuthorizationError
from mitama.nodes import User
import urllib

meta = Metadata()

@middleware
async def initialize_middleware(request, handler):
    if User.query.count() == 0:
        return Response(headers = {
            'Location': app.convert_uri('/setup')
        })
    else:
        return await handler(request)

@middleware
async def session_middleware(request, handler):
    try:
        await get_login_state(request)
    except AuthorizationError:
        if app.revert_uri(request.url).path != '/login':
            return Response.redirect(app.convert_uri('/login?'+urllib.parse.quote(str(request.url))), status = 301)
    return await handler(request)

app = App(meta, middlewares = [initialize_middleware, session_middleware])
app.router.add_routes(urls.urls)
