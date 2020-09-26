from mitama.http import Request, Response
import copy
import re

class RoutingError(Exception):
    pass

class Router():
    app = None
    def __init__(self, routes = [], middlewares = [], prefix = ''):
        self.routes = routes
        self.middlewares = list()
        self.prefix = prefix
        for middleware in middlewares:
            self.middlewares.append(middleware)
        self.i = 0
    def add_route(self, route):
        self.routes.append(route)
    def add_routes(self, routes):
        self.routes.extend(routes)
    def add_middleware(self, middleware):
        self.middlewares.append(middleware)
    def add_middlewares(self, middlewares):
        self.middlewares.extend(middlewares)
    def clone(self, prefix = None):
        return Router(
            routes = copy.copy(self.routes),
            prefix = self.prefix if prefix == None else prefix
        )
    async def match(self, request):
        method = request.method
        path = request.subpath if hasattr(request, 'subpath') else request.path
        if self.prefix != '' and self.prefix != '/':
            if path[:len(self.prefix)] != self.prefix:
                return False
            else:
                path = path[len(self.prefix):]
                request.subpath = path
        for route in self.routes:
            result = await route.match(request)
            if result != False:
                request, result = result
                def get_response_handler(result):
                    i = 0
                    async def handle(request):
                        nonlocal i
                        if i>=len(self.middlewares) or len(self.middlewares) == 0:
                            if callable(result):
                                return await result(request)
                            elif callable(getattr(result, 'handle')):
                                return await result.handle(request)
                            else:
                                raise RoutingError('Unsupported interface object. Only callables and Controller instances are supported.')
                        else:
                            middleware = self.middlewares[i]
                            i += 1
                            return await middleware.process(request, handle)
                    return handle
                handler = get_response_handler(result)
                return request, handler
        return False

class Route():
    def __init__(self, methods, path, handler):
        self.methods = methods
        self.path = Path(path)
        self.handler = handler
        pass
    async def match(self, request):
        method = request.method
        path = request.subpath if hasattr(request, 'subpath') else request.path
        args = self.path.match(path)
        if method in self.methods and args != False:
            request.params = args
            return request, self.handler
        else:
            return False

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
