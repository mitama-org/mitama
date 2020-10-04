from mitama.app.router import Route, GroupRoute

def view(path, handler, method = None):
    '''GET, POSTのルーティング先を指定

    ブラウザで見れる一般的なルーティング先を作成します。
    :param path: マッチするパス
    :param handler: リクエストハンドラ
    :return: Routeインスタンス
    '''
    return Route(['GET', 'POST'], path, handler, method)

def any(path, handler, method = None):
    '''メソッドを考慮しないルーティング先を指定

    メソッドに関係なくマッチするルーティング先を作成します。
    :param path: マッチするパス
    :param handler: リクエストハンドラ
    :return: Routeインスタンス
    '''
    return Route(['GET', 'POST', 'PATCH', 'PUT', 'DELETE', 'OPTION', 'HEAD'], path, handler, method)

def post(path, handler, method = None):
    '''POSTのルーティング先を指定

    POSTメソッドのルーティング先を作成します。
    :param path: マッチするパス
    :param handler: リクエストハンドラ
    :return: Routeインスタンス
    '''
    return Route(['POST'], path, handler, method)

def patch(path, handler, method = None):
    '''PATCHのルーティング先を指定

    PATCHメソッドのルーティング先を作成します。
    :param path: マッチするパス
    :param handler: リクエストハンドラ
    :return: Routeインスタンス
    '''
    return Route(['PATCH'], path, handler, method)

def head(path, handler, method = None):
    '''HEADのルーティング先を指定

    HEADメソッドのルーティング先を作成します。
    :param path: マッチするパス
    :param handler: リクエストハンドラ
    :return: Routeインスタンス
    '''
    return Route(['HEAD'], path, handler, method)

def option(path, handler, method = None):
    '''OPTIONのルーティング先を指定

    OPTIONメソッドのルーティング先を作成します。
    :param path: マッチするパス
    :param handler: リクエストハンドラ
    :return: Routeインスタンス
    '''
    return Route(['OPTION'], path, handler, method)

def put(path, handler, method = None):
    '''PUTのルーティング先を指定

    PUTメソッドのルーティング先を作成します。
    :param path: マッチするパス
    :param handler: リクエストハンドラ
    :return: Routeインスタンス
    '''
    return Route(['PUT'], path, handler, method)

def get(path, handler, method = None):
    '''GETのルーティング先を指定

    GETメソッドのルーティング先を作成します。
    :param path: マッチするパス
    :param handler: リクエストハンドラ
    :return: Routeインスタンス
    '''
    return Route(['GET'], path, handler, method)

def delete(path, handler, method = None):
    '''DELETEのルーティング先を指定

    DELETEメソッドのルーティング先を作成します。
    :param path: マッチするパス
    :param handler: リクエストハンドラ
    :return: Routeインスタンス
    '''
    return Route(['DELETE'], path, handler, method)

def group(path, router):
    '''グループルーティング先を指定

    前方一致でルーティング先に中継するルーティング先を作成します。
    :param path: マッチするパス
    :param router: 渡すルーティングエンジン
    :return: GroupRouteインスタンス
    '''
    return GroupRoute(path, router)

