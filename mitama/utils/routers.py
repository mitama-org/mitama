from mitama.app import Router
from mitama.app.method import *

from .controllers import GroupCRUDController, UserCRUDController
from .middlewares import SessionMiddleware


def create_api_router(middlewares=[SessionMiddleware]):
    return Router(
        [
            post("/users", UserCRUDController, "create"),
            post("/groups", GroupCRUDController, "create"),
        ],
        middlewares,
    )


def retrieve_api_router(middlewares=[]):
    return Router(
        [
            get("/users", UserCRUDController, "list"),
            get("/users/<id>", UserCRUDController, "retrieve"),
            get("/users/<id>/icon", UserCRUDController, "icon"),
            get("/groups", GroupCRUDController, "list"),
            get("/groups/<id>", GroupCRUDController, "retrieve"),
            get("/groups/<id>/icon", GroupCRUDController, "icon"),
        ],
        middlewares,
    )


def update_api_router(middlewares=[SessionMiddleware]):
    return Router(
        [
            post("/users/<id>", UserCRUDController, "update"),
            post("/groups/<id>", GroupCRUDController, "update"),
        ],
        middlewares,
    )


def delete_api_router(middlewares=[SessionMiddleware]):
    return Router(
        [
            delete("/users/<id>", UserCRUDController, "delete"),
            delete("/groups/<id>", GroupCRUDController, "delete"),
        ],
        middlewares,
    )


def rest_api_router(middlewares=[SessionMiddleware]):
    return Router(
        [
            post("/users", UserCRUDController, "create"),
            post("/groups", GroupCRUDController, "create"),
            get("/users", UserCRUDController, "list"),
            get("/users/<id>", UserCRUDController, "retrieve"),
            get("/groups", GroupCRUDController, "list"),
            get("/groups/<id>", GroupCRUDController, "retrieve"),
            post("/users/<id>", UserCRUDController, "update"),
            post("/groups/<id>", GroupCRUDController, "update"),
            delete("/users/<id>", UserCRUDController, "delete"),
            delete("/groups/<id>", GroupCRUDController, "delete"),
        ],
        middlewares,
    )
