import copy
import inspect
import re

from .http import Request, Response


class RoutingError(Exception):
    pass


class Router:
    """ルーティングエンジン

    手軽に実装できて必要最低限なものを目指したので、遅かったりして嫌いだったら無理にこれを使う必要はありません。
    自前のものを適用したい場合は、とりあえず:samp:`hoge.match(Request): -> Response` といったインターフェースを実装したメソッドを作ってください。
    routesの中にRouterインスタンスを指定することもできます。
    """

    _app = None

    def __init__(self, routes=[], middlewares=[]):
        """初期化処理

        :param routes: Router、またはRouteのリスト
        :param middlewares: Middlewareのリスト
        """
        self._parent = None
        self.routes = list()
        self.middlewares = list()
        self.add_routes(routes)
        self.add_middlewares(middlewares)
        self.i = 0

    def add_route(self, route):
        """ルーティング先を追加します

        mitama.app.methodの関数で生成したRouteインスタンスを与えてください。
        :param route: Routeインスタンス
        """
        if isinstance(route, Router):
            route._parent = self
        self.routes.append(route)

    def add_routes(self, routes):
        """複数のルーティング先を追加します

        mitama.app.methodの関数で生成したRouteインスタンスを与えてください。
        :param routes: Routeインスタンスのリスト
        """
        for route in routes:
            self.add_route(route)

    def add_middleware(self, middleware):
        """ミドルウェアを登録します

        Middlewareクラスを与えると、このルーターのインスタンス内でマッチした場合にミドルウェアが順番に起動します。
        :param middleware: Middlewareのインスタンス
        """
        self.middlewares.append(middleware)

    def add_middlewares(self, middlewares):
        """複数のミドルウェアを登録します

        Middlewareクラスのリストを与えると、このルーターのインスタンス内でマッチした場合にミドルウェアが順番に起動します。
        :param middlewares: Middlewareのインスタンスのリスト
        """
        for middleware in middlewares:
            self.add_middleware(middleware)

    def clone(self):
        return Router(routes=copy.copy(self.routes))

    def match(self, request):
        method = request.method
        path = request.subpath if hasattr(request, "subpath") else request.path
        paths_to_check = [path]
        paths_to_check.append(re.sub("//+", "/", path))
        if not request.path.endswith("/"):
            paths_to_check.append(path + "/")
        paths_to_check.append(re.sub("//+", "/", path + "/"))
        if path.endswith("/"):
            merged_slashes = re.sub("//+", "/", path)
            paths_to_check.append(merged_slashes[:-1])

        for path in paths_to_check:
            for route in self.routes:
                request.subpath = path
                result = route.match(request)
                if result != False:
                    request, result, method = result

                    def get_response_handler(result, method):
                        i = 0

                        def handle(request):
                            nonlocal i
                            nonlocal result
                            if inspect.isclass(result):
                                result = result(request.app)
                                if method is not None:
                                    inst = result

                                    def result(request):
                                        return inst(request, method)

                            if i >= len(self.middlewares) or len(self.middlewares) == 0:
                                if callable(result):
                                    return result(request)
                                else:
                                    raise RoutingError(
                                        "Unsupported interface object. Only callables and Controller instances are supported."
                                    )
                            else:
                                if hasattr(request, "app"):
                                    middleware = self.middlewares[i](request.app)
                                else:
                                    middleware = self.middlewares[i]()
                                i += 1
                                return middleware.process(request, handle)

                        return handle

                    handler = get_response_handler(result, method)
                    return request, handler, None
        return False
