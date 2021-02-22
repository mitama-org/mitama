import urllib
import base64
from secrets import token_hex

from mitama.app import Middleware
from mitama.app.http import Response
from mitama.models import User


class SessionMiddleware(Middleware):
    """ログイン判定ミドルウェア

    ログインしていないユーザーがアクセスした場合、/login?redirect_to=<URL>にリダイレクトします。
    """

    def process(self, request, handler):
        sess = request.session()
        try:
            if "jwt_token" in sess:
                request.user = User.check_jwt(sess["jwt_token"])
            else:
                return Response.redirect(
                    "/login?redirect_to="
                    + urllib.parse.quote(str(request.url), safe="")
                )
        except Exception as err:
            return Response.redirect(
                "/login?redirect_to=" + urllib.parse.quote(str(request.url), safe="")
            )
        return handler(request)

class BasicMiddleware(Middleware):
    """BASIC認証ミドルウェア"""

    def process(self, request, handler):
        try:
            if "HTTP_AUTHORIZATION" in request.headers:
                name, token = request.headers["HTTP_AUTHORIZATION"].split(" ")
                login, password = base64.b64decode(token).decode().split(":")
                request.user = User.password_auth(login, password)
            else:
                return Response(status=401, reason="Authorization Required", headers = {
                    "WWW-Authenticate": "Basic realm=\"mitama authorization\""
                })
        except Exception as err:
            print(err)
            return Response(status=401, reason="Authorization Required", headers = {
                "WWW-Authenticate": "Basic realm=\"mitama authorization\""
            })
        return handler(request)

class CsrfMiddleware(Middleware):
    def process(self, request, handler):
        sess = request.session()
        if request.method == "POST":
            session_token = sess["mitama_csrf_token"]
            posts = request.post()
            if "mitama_csrf_token" not in posts:
                return Response(status=400, reason="Bad Request")
            post_token = posts["mitama_csrf_token"]
            if session_token != post_token:
                return Response(status=400, reason="Bad Request")
        else:
            sess["mitama_csrf_token"] = token_hex(16)
        return handler(request)
