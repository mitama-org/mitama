import urllib
import base64

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
