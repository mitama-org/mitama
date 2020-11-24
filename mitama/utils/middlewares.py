import urllib

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
