from mitama.http import Request, Response
import inspect
import copy
import re

class RoutingError(Exception):
    pass


class Router():
    '''ルーティングエンジン

    手軽に実装できて必要最低限なものを目指したので、遅かったりして嫌いだったら無理にこれを使う必要はありません。
    自前のものを適用したい場合は、とりあえず:samp:`hoge.match(Request): -> Response` といったインターフェースを実装したメソッドを作ってください。
    routesの中にRouterインスタンスを指定することもできます。
    '''
    _app = None
    def __init__(self, routes = [], middlewares = [], prefix = ''):
        '''初期化処理

        :param routes: Router、またはRouteのリスト
        :param middlewares: Middlewareのリスト
        '''
        self._parent = None
        self.routes = list()
        self.middlewares = list()
        self.add_routes(routes)
        self.add_middlewares(middlewares)
        self.i = 0
    def add_route(self, route):
        '''ルーティング先を追加します

        mitama.app.methodの関数で生成したRouteインスタンスを与えてください。
        :param route: Routeインスタンス
        '''
        if isinstance(route, Router):
            route._parent = self
        self.routes.append(route)
    def add_routes(self, routes):
        '''複数のルーティング先を追加します

        mitama.app.methodの関数で生成したRouteインスタンスを与えてください。
        :param routes: Routeインスタンスのリスト
        '''
        for route in routes:
            self.add_route(route)
    def add_middleware(self, middleware):
        '''ミドルウェアを登録します

        Middlewareクラスを与えると、このルーターのインスタンス内でマッチした場合にミドルウェアが順番に起動します。
        :param middleware: Middlewareのインスタンス
        '''
        self.middlewares.append(middleware)
    def add_middlewares(self, middlewares):
        '''複数のミドルウェアを登録します

        Middlewareクラスのリストを与えると、このルーターのインスタンス内でマッチした場合にミドルウェアが順番に起動します。
        :param middlewares: Middlewareのインスタンスのリスト
        '''
        for middleware in middlewares:
            self.add_middleware(middleware)
    def clone(self):
        return Router(routes = copy.copy(self.routes))
    def match(self, request):
        method = request.method
        path = request.subpath if hasattr(request, 'subpath') else request.path
        paths_to_check = [path]
        paths_to_check.append(re.sub('//+', '/', path))
        if not request.path.endswith('/'):
            paths_to_check.append(path + '/')
        paths_to_check.append(
            re.sub('//+', '/', path + '/'))
        if path.endswith('/'):
            merged_slashes = re.sub('//+', '/', path)
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
                            if i>=len(self.middlewares) or len(self.middlewares) == 0:
                                if callable(result):
                                    return result(request)
                                else:
                                    raise RoutingError('Unsupported interface object. Only callables and Controller instances are supported.')
                            else:
                                if hasattr(request, 'app'):
                                    middleware = self.middlewares[i](request.app)
                                else:
                                    middleware = self.middlewares[i]()
                                i += 1
                                return middleware.process(request, handle)
                        return handle
                    handler = get_response_handler(result, method)
                    return request, handler, None
        return False

class Route():
    def __init__(self, methods, path, handler, method_name):
        self.methods = methods
        self.path = Path(path)
        self.handler = handler
        self.method_name = method_name
        pass
    def match(self, request):
        method = request.method
        path = request.subpath if hasattr(request, 'subpath') else request.path
        args = self.path.match(path)
        if method in self.methods and args != False:
            request.params = args
            return request, self.handler, self.method_name
        else:
            return False

class GroupRoute():
    def __init__(self, path, router):
        self.path = path
        self.router = router
        pass
    def match(self, request):
        path = request.subpath if hasattr(request, 'subpath') else request.path
        if str(self.path) != '' and str(self.path) != '/':
            if path[:len(self.path)] != self.path:
                return False
            else:
                path = path[len(self.path):]
                request.subpath = path
        return self.router.match(request)

def _re_flatten(p):
    if '(' not in p:
        return p
    return re.sub(
        r'(\\*)(\(\?P<[^>]+>|\((?!\?))',
        lambda m: m.group(0) if len(m.group(1)) % 2 else m.group(1) + '(?:',
        p
    )

class Path():
    rule_syntax = re.compile('(\\\\*)(?:(?:<([a-zA-Z_][a-zA-Z_0-9]*)?(?::([a-zA-Z_]*)(?::((?:\\\\.|[^\\\\>])+)?)?)?>))')
    filters = {
        're': lambda conf: (_re_flatten(conf or '[^/]+'), None, None),
        'int': lambda conf: (r'-?\d+', int, lambda x: str(int(x))),
        'float': lambda conf: (r'-?[\d.]+', float, lambda x: str(float(x))),
        'path': lambda conf: (r'.+?', None, None)
    }
    default_filter = 're'
    def __init__(self, path):
        self.raw = path
        self.builder = []
        anons = 0
        pattern = ''
        keys = []
        filters = []
        is_static = True
        for key, mode, conf in self._itertoken(path):
            if mode:
                is_static = False
                if mode == 'default':
                    mode = self.default_filter
                mask, in_filter, out_filter = self.filters[mode](conf)
                if not key:
                    pattern+='(?:%s)' % mask
                    key = 'anon%d' % anons
                    anons += 1
                else:
                    pattern += '(?P<%s>%s)' % (key, mask)
                    keys.append(key)
                if in_filter:
                    filters.append((key, in_filter))
            elif key:
                pattern += re.escape(key)

        try:
            re_pattern = re.compile('^(%s)$' % pattern)
            re_match = re_pattern.match
        except re.error as e:
            raise RouteSyntaxError('')

        if filters:
            def getargs(path):
                url_args = re_match(path).groupdict()
                for name, wildcard_filter in filters:
                    try:
                        url_args[name] = wildcard_filter(url_args[name])
                    except ValueError:
                        raise RoutingError()
                return url_args
        elif re_pattern.groupindex:
            def getargs(path):
                return re_match(path).groupdict()
        else:
            getargs = None
        flatpat = _re_flatten(pattern)
        self.rule = (path, re.compile('(^%s$)' % flatpat), getargs)
    def _itertoken(self, path):
        offset = 0
        prefix = ''
        for match in self.rule_syntax.finditer(path):
            prefix += path[offset:match.start()]
            g = match.groups()
            if len(g[0]) % 2:
                prefix += match.group(0)[len(g[0]):]
                offset = match.end()
                continue
            if prefix:
                yield prefix, None, None
            name, filtr, conf = g[1:4]
            yield name, filtr or 'default', conf or None
            offset, prefix = match.end(), ''
        if offset<=len(path) or prefix:
            yield prefix + path[offset:], None, None
    def match(self, target):
        path, flatpat, getargs = self.rule
        if flatpat.match(target) != None:
            return getargs(target) if getargs else {}
        else:
            return False
