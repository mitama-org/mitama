import sys
import importlib
import subprocess
import mitama
import inspect
import smtplib
from email.mime.text import MIMEText
import json
from mitama.app.http import Request
from mitama.app import App, AppRegistry
from mitama.app.app import _session_middleware
from mitama.db import create_engine, DatabaseManager
from mitama.conf import get_from_project_dir


class Project(App):
    def __init__(self):
        config = get_from_project_dir()

        if config.database["type"] == "mysql":
            engine = create_engine(
                "mysql://{}:{}@{}/{}".format(
                    config.database["user"],
                    config.database["password"],
                    config.database["host"],
                    config.database["name"]
                ),
                encoding="utf8"
            )
        elif config.database["type"] == "postgresql":
            engine = create_engine(
                "postgresql://{}:{}@{}/{}".format(
                    config.database["user"],
                    config.database["password"],
                    config.database["host"],
                    config.database["name"]
                ),
                encoding="utf8",
                echo=True
            )
        else:
            engine = create_engine("sqlite:///" + str(config.database["path"]))
        DatabaseManager.set_engine(engine)

        from mitama.models import User, Group
        User._project = self
        Group._project = self
        self.port = config.port
        self.mail = config.mail
        self.password_validation = config.password_validation
        self.project_dir = config._project_dir
        self.apps = AppRegistry()
        self.apps.project = self
        self.apps.load_config(config)
        self.middlewares = [_session_middleware()]
        self.config = config

    def __call__(self, env, start_response):
        request = Request(env)
        result  = self.match(request)
        if result:
            request, handler = result
            response = handler(request)
        else:
            response = self.error(request, 404)
        body = response.start(request, start_response)
        return body

    def send_mail(self, to, subject, body, type="html"):
        mail = self.mail
        smtp = smtplib.SMTP(mail["host"], mail["port"])
        if smtp.has_extn("STARTTLS"):
            smtp.starttls()
        if "user" in mail:
            smtp.login(mail["user"]["login"], mail["user"]["password"])
        msg = MIMEText(body, type)
        msg["Subject"] = subject
        msg["To"] = to
        msg["From"] = mail["address"]
        smtp.send_message(msg)
        smtp.quit()

    def match(self, request):
        for app_name, app in self.apps.items():
            path_ = app.path
            if path_[0] != "/":
                path_ = "/" + path_
            if request.path.startswith(path_):
                request.app = app
                result = app
                method = request.method
                path = request.subpath if hasattr(request, "subpath") else request.path
                request.subpath = path[len(path_):] if path_ != "/" else path
                def get_response_handler(result, method):
                    i = 0

                    def handle(request):
                        nonlocal i
                        nonlocal result
                        if inspect.isclass(result):
                            result = result(request.app)
                            if method is not None:
                                inst = result

                                def result(request):
                                    return inst(request, method)

                        if i >= len(self.middlewares) or len(self.middlewares) == 0:
                            if callable(result):
                                return result(request)
                            else:
                                raise RoutingError(
                                    "Unsupported interface object. Only callables and Controller instances are supported."
                                )
                        else:
                            middleware = self.middlewares[i]()
                            i += 1
                            return middleware.process(request, handle)

                    return handle

                handler = get_response_handler(result, method)
                return request, handler
        return False

    def install(self, package_name, path="/"):
        app = self.apps.load_package(package_name, path, self._project_dir)
        self.apps[path] = app
        self.apps[path].install()
        self.config[package_name] = {
            "path": path
        }
        with open("mitama.json", "w") as f:
            f.write(json.dumps(self.config.to_dict()))

    def uninstall(self, package_name):
        self.apps[package_name].uninstall()
        del self.apps[package_name]
        del self.config[package_name]
        with open("mitama.json", "w") as f:
            f.write(json.dumps(self.config.to_dict()))
