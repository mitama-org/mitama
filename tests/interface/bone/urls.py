from mitama.http.method import *
from . import views

urls = [
    view('/', views.welcome)
]
