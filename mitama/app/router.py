from mitama.http import Response

class RoutingError(Exception):
    pass

class Router():
    app = None
    def __init__(self, routes, middlewares = []):
        self.routes = routes
        self.middlewares = list()
        for middleware in middlewares:
            self.middlewares.append(middleware)
        self.i = 0
    async def match(self, request):
        method = request.method
        path = request.path
        for route in self.routes:
            result = await route.match(request)
            if result.__class__.__name__ == 'Response':
                return result
            if result != False:
                def get_response_handler(result):
                    i = 0
                    async def handle(request):
                        nonlocal i
                        if i>=len(self.middlewares) or len(self.middlewares) == 0:
                            if callable(result):
                                return await result(request)
                            elif callable(getattr(result, 'handler')):
                                return await result.handler(request)
                            else:
                                raise RoutingError('Unsupported interface object. Only callables and Controller instances are supported.')
                        else:
                            middleware = self.middlewares[i]
                            i += 1
                            return await middleware.process(request, handle)
                    return handle
                handler = get_response_handler(result)
                return await handler(request)
        return Response(status = 404)

class Route():
    def __init__(self, methods, path, handler):
        self.methods = methods
        self.path = Path(path)
        self.handler = handler
        pass
    async def match(self, request):
        method = request.method
        path = request.path
        if method in self.methods and self.path.match(path) != False:
            return self.handler
        else:
            return False

class Path():
    def __init__(self, path):
        self.raw = path
        dirs = str(path).split('/')
        self.dirs = list()
        for d in dirs: 
            if len(d) > 0 and d[0] == '{' and d[-1] == '}':
                self.dirs.append({
                    'type': 'arg',
                    'name': d[1:-2]
                })
            else:
                self.dirs.append({
                    'type': 'fs',
                    'name': d
                })
    def match(self, path):
        dirs = str(path).split('/')
        if len(dirs) != len(self.dirs):
            return False
        else:
            args = dict()
            for i in range(len(self.dirs)):
                if self.dirs[i]['type'] == 'arg':
                    args[self.dirs[i]['name']] = dirs[i]
                elif self.dirs[i]['name'] != dirs[i]:
                    return False
            return args
