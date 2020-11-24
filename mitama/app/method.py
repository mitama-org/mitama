import re


class _Route:
    def __init__(self, methods, path, handler, method_name):
        self.methods = methods
        self.path = _Path(path)
        self.handler = handler
        self.method_name = method_name
        pass

    def match(self, request):
        method = request.method
        path = request.subpath if hasattr(request, "subpath") else request.path
        args = self.path.match(path)
        if method in self.methods and args != False:
            request.params = args
            return request, self.handler, self.method_name
        else:
            return False


class _GroupRoute:
    def __init__(self, path, router):
        self.path = path
        self.router = router
        pass

    def match(self, request):
        path = request.subpath if hasattr(request, "subpath") else request.path
        if str(self.path) != "" and str(self.path) != "/":
            if path[: len(self.path)] != self.path:
                return False
            else:
                path = path[len(self.path) :]
                request.subpath = path
        return self.router.match(request)


def _re_flatten(p):
    if "(" not in p:
        return p
    return re.sub(
        r"(\\*)(\(\?P<[^>]+>|\((?!\?))",
        lambda m: m.group(0) if len(m.group(1)) % 2 else m.group(1) + "(?:",
        p,
    )


class _Path:
    rule_syntax = re.compile(
        "(\\\\*)(?:(?:<([a-zA-Z_][a-zA-Z_0-9]*)?(?::([a-zA-Z_]*)(?::((?:\\\\.|[^\\\\>])+)?)?)?>))"
    )
    filters = {
        "re": lambda conf: (_re_flatten(conf or "[^/]+"), None, None),
        "int": lambda conf: (r"-?\d+", int, lambda x: str(int(x))),
        "float": lambda conf: (r"-?[\d.]+", float, lambda x: str(float(x))),
        "path": lambda conf: (r".+?", None, None),
    }
    default_filter = "re"

    def __init__(self, path):
        self.raw = path
        self.builder = []
        anons = 0
        pattern = ""
        keys = []
        filters = []
        is_static = True
        for key, mode, conf in self._itertoken(path):
            if mode:
                is_static = False
                if mode == "default":
                    mode = self.default_filter
                mask, in_filter, out_filter = self.filters[mode](conf)
                if not key:
                    pattern += "(?:%s)" % mask
                    key = "anon%d" % anons
                    anons += 1
                else:
                    pattern += "(?P<%s>%s)" % (key, mask)
                    keys.append(key)
                if in_filter:
                    filters.append((key, in_filter))
            elif key:
                pattern += re.escape(key)

        try:
            re_pattern = re.compile("^(%s)$" % pattern)
            re_match = re_pattern.match
        except re.error as e:
            raise _RouteSyntaxError("")

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
        self.rule = (path, re.compile("(^%s$)" % flatpat), getargs)

    def _itertoken(self, path):
        offset = 0
        prefix = ""
        for match in self.rule_syntax.finditer(path):
            prefix += path[offset : match.start()]
            g = match.groups()
            if len(g[0]) % 2:
                prefix += match.group(0)[len(g[0]) :]
                offset = match.end()
                continue
            if prefix:
                yield prefix, None, None
            name, filtr, conf = g[1:4]
            yield name, filtr or "default", conf or None
            offset, prefix = match.end(), ""
        if offset <= len(path) or prefix:
            yield prefix + path[offset:], None, None

    def match(self, target):
        path, flatpat, getargs = self.rule
        if flatpat.match(target) != None:
            return getargs(target) if getargs else {}
        else:
            return False


def view(path, handler, method=None):
    """GET, POSTのルーティング先を指定

    ブラウザで見れる一般的なルーティング先を作成します。
    :param path: マッチするパス
    :param handler: リクエストハンドラ
    :return: _Routeインスタンス
    """
    return _Route(["GET", "POST"], path, handler, method)


def any(path, handler, method=None):
    """メソッドを考慮しないルーティング先を指定

    メソッドに関係なくマッチするルーティング先を作成します。
    :param path: マッチするパス
    :param handler: リクエストハンドラ
    :return: _Routeインスタンス
    """
    return _Route(
        ["GET", "POST", "PATCH", "PUT", "DELETE", "OPTION", "HEAD"],
        path,
        handler,
        method,
    )


def post(path, handler, method=None):
    """POSTのルーティング先を指定

    POSTメソッドのルーティング先を作成します。
    :param path: マッチするパス
    :param handler: リクエストハンドラ
    :return: _Routeインスタンス
    """
    return _Route(["POST"], path, handler, method)


def patch(path, handler, method=None):
    """PATCHのルーティング先を指定

    PATCHメソッドのルーティング先を作成します。
    :param path: マッチするパス
    :param handler: リクエストハンドラ
    :return: _Routeインスタンス
    """
    return _Route(["PATCH"], path, handler, method)


def head(path, handler, method=None):
    """HEADのルーティング先を指定

    HEADメソッドのルーティング先を作成します。
    :param path: マッチするパス
    :param handler: リクエストハンドラ
    :return: _Routeインスタンス
    """
    return _Route(["HEAD"], path, handler, method)


def option(path, handler, method=None):
    """OPTIONのルーティング先を指定

    OPTIONメソッドのルーティング先を作成します。
    :param path: マッチするパス
    :param handler: リクエストハンドラ
    :return: _Routeインスタンス
    """
    return _Route(["OPTION"], path, handler, method)


def put(path, handler, method=None):
    """PUTのルーティング先を指定

    PUTメソッドのルーティング先を作成します。
    :param path: マッチするパス
    :param handler: リクエストハンドラ
    :return: _Routeインスタンス
    """
    return _Route(["PUT"], path, handler, method)


def get(path, handler, method=None):
    """GETのルーティング先を指定

    GETメソッドのルーティング先を作成します。
    :param path: マッチするパス
    :param handler: リクエストハンドラ
    :return: _Routeインスタンス
    """
    return _Route(["GET"], path, handler, method)


def delete(path, handler, method=None):
    """DELETEのルーティング先を指定

    DELETEメソッドのルーティング先を作成します。
    :param path: マッチするパス
    :param handler: リクエストハンドラ
    :return: _Routeインスタンス
    """
    return _Route(["DELETE"], path, handler, method)


def group(path, router):
    """グループルーティング先を指定

    前方一致でルーティング先に中継するルーティング先を作成します。
    :param path: マッチするパス
    :param router: 渡すルーティングエンジン
    :return: _GroupRouteインスタンス
    """
    return _GroupRoute(path, router)
