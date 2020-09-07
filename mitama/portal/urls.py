import os
from pathlib import Path
from mitama.http.method import *
from . import views
from .views import user
from .views import group

project_dir = Path(os.path.dirname(__file__))

urls = [
    static('/assets', project_dir / 'static'),
    view('/', views.home),
    view('/login', views.login),
    view('/signup', views.signup),
    view('/users', user.list),
    view('/users/invite', user.create),
    view('/users/{id}', user.retrieve),
    view('/users/{id}/settings', user.update),
    view('/users/{id}/delete', user.delete),
    view('/groups', group.list),
    view('/groups/create', group.create),
    view('/groups/{id}', group.retrieve),
    view('/groups/{id}/settings', group.update),
    view('/groups/{id}/delete', group.delete),
]
