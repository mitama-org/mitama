from mitama.http.method import *
from . import views

urls = [
    view('/', views.home),
    view('/login', views.login),
    view('/setup', views.setup),
    view('/signup', views.signup),
]
