from mitama.app import App, Router, StaticFileController
from mitama.app.method import view
from .controller import WelcomeController

welcome = WelcomeController()
static = StaticFileController()

class App(App):
    #name = 'MyApp'
    #description = 'This is my App.'
    instances = [
        welcome,
        static
    ]
    router = Router([
        view('/', welcome),
        view('/static/<path:path>', static),
    ])
