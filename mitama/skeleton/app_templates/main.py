from mitama.app import App, Router
from mitama.utils.controllers import static_files
from mitama.app.method import view

from .controller import WelcomeController


class App(App):
    # name = 'MyApp'
    # description = 'This is my App.'
    router = Router(
        [
            view("/", WelcomeController),
            view("/static/<path:path>", static_files()),
        ]
    )
