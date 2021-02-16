import sys
import importlib
import subprocess
from mitama.app import App

class Project(App):
    def __init__(self):
        config = get_from_project_dir()
        self.port = config.port
        self.apps = AppRegistry()
        self.apps.load_config(config)

    def __call__(self, env, start_response):
        request = Request(env)
        app = self.match(request.path)
        response = app(request)
        body = response.start(request, start_response)
        return body

    def match(self, path):
        for app_path, app in self.apps.items():
            if app_path[0] != "/":
                app_path = "/" + app_path
            if path.startswith(app_path):
                return app
        self.error(404)

    def uninstall(self, package_name):
        self.apps[package_name].uninstall()
        del self.apps[package_name]
