from mitama.app.router import Route
from mitama.app import StaticFileController

def view(path, handler):
    return Route(['GET', 'POST'], path,handler)

def static(path, dirname):
    return Route(['GET', 'POST'], path, StaticFileController(dirname))

def post(path, handler):
    return Route(['POST'], path,handler)

def patch(path, handler):
    return Route(['PATCH'], path,handler)

def head(path, handler):
    return Route(['HEAD'], path,handler)

def option(path, handler):
    return Route(['OPTION'], path,handler)

def put(path, handler):
    return Route(['PUT'], path,handler)

def get(path, handler):
    return Route(['GET'], path,handler)

def delete(path, handler):
    return Route(['DELETE'], path,handler)
