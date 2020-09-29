from mitama.app.router import Route

def view(path, handler):
    '''GET, POSTのルーティング先を指定

    ブラウザで見れる一般的なルーティング先を作成します。
    :param path: マッチするパス
    :param handler: リクエストハンドラ
    :return: Routeインスタンス
    '''
    return Route(['GET', 'POST'], path, handler)

def any(path, handler):
    '''メソッドを考慮しないルーティング先を指定

    メソッドに関係なくマッチするルーティング先を作成します。
    :param path: マッチするパス
    :param handler: リクエストハンドラ
    :return: Routeインスタンス
    '''
    return Route(['GET', 'POST', 'PATCH', 'PUT', 'DELETE', 'OPTION', 'HEAD'], path, handler)

def post(path, handler):
    '''POSTのルーティング先を指定

    POSTメソッドのルーティング先を作成します。
    :param path: マッチするパス
    :param handler: リクエストハンドラ
    :return: Routeインスタンス
    '''
    return Route(['POST'], path, handler)

def patch(path, handler):
    '''PATCHのルーティング先を指定

    PATCHメソッドのルーティング先を作成します。
    :param path: マッチするパス
    :param handler: リクエストハンドラ
    :return: Routeインスタンス
    '''
    return Route(['PATCH'], path, handler)

def head(path, handler):
    '''HEADのルーティング先を指定

    HEADメソッドのルーティング先を作成します。
    :param path: マッチするパス
    :param handler: リクエストハンドラ
    :return: Routeインスタンス
    '''
    return Route(['HEAD'], path, handler)

def option(path, handler):
    '''OPTIONのルーティング先を指定

    OPTIONメソッドのルーティング先を作成します。
    :param path: マッチするパス
    :param handler: リクエストハンドラ
    :return: Routeインスタンス
    '''
    return Route(['OPTION'], path, handler)

def put(path, handler):
    '''PUTのルーティング先を指定

    PUTメソッドのルーティング先を作成します。
    :param path: マッチするパス
    :param handler: リクエストハンドラ
    :return: Routeインスタンス
    '''
    return Route(['PUT'], path, handler)

def get(path, handler):
    '''GETのルーティング先を指定

    GETメソッドのルーティング先を作成します。
    :param path: マッチするパス
    :param handler: リクエストハンドラ
    :return: Routeインスタンス
    '''
    return Route(['GET'], path, handler)

def delete(path, handler):
    '''DELETEのルーティング先を指定

    DELETEメソッドのルーティング先を作成します。
    :param path: マッチするパス
    :param handler: リクエストハンドラ
    :return: Routeインスタンス
    '''
    return Route(['DELETE'], path, handler)

