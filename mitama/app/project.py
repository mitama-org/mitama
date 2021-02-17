import sys
import importlib
import subprocess
import mitama
import inspect
from mitama.app.http import Request
from mitama.app import App, AppRegistry
from mitama.app.app import _session_middleware
from mitama.db import create_engine, DatabaseManager
from mitama.conf import get_from_project_dir


class Project(App):
    def __init__(self):
        config = get_from_project_dir()

        engine = create_engine("sqlite:///" + str(config._sqlite_db_path))
        DatabaseManager.set_engine(engine)

        from mitama.models import User, Group
        User._project = self
        Group._project = self
        self.port = config.port
        self.mail = config.mail
        self.apps = AppRegistry()
        self.apps.load_config(config)
        self.middlewares = [_session_middleware()]

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
        for path, app in self.apps.items():
            if path[0] != "/":
                path = "/" + path
            if request.path.startswith(path):
                request.app = app
                result = app
                method = request.method
                path = request.subpath if hasattr(request, "subpath") else request.path
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


    def uninstall(self, package_name):
        self.apps[package_name].uninstall()
        del self.apps[package_name]
