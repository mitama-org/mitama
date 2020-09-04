from mitama.http.method import *
from . import views

urls = [
    view('/', views.home),
    view('/login', views.login),
    view('/signup', views.signup),
]
