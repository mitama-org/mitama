from . import views
from mitama.http.method import *

urls = [
    view('/', views.home),
    view('/about', views.about)
]
