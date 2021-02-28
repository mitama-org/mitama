#!/usr/bin/python
import os
from base64 import b64encode
from pathlib import Path

import magic
import markdown
from jinja2 import Markup, Environment, ChoiceLoader, FileSystemLoader
from yarl import URL
import uuid

from mitama.noimage import load_noimage_app

from .http import Request, Response


def dataurl(blob):
    f = magic.Magic(mime=True, uncompress=True)
    mime = f.from_buffer(blob)
    return "data:" + mime + ";base64," + b64encode(blob).decode()


class App:
    template_dir = "templates"
    description = ""
    name = ""
    models = list()

    @property
    def icon(self):
        return load_noimage_app()

    def __init__(self, screen_name, path, package, project_dir=None, install_dir=os.path.dirname(__file__), **kwargs):
        self.screen_name = screen_name
        self.path = path
        self.package = package
        self.project_dir = Path(project_dir)
        self.install_dir = Path(install_dir)
        self.params = kwargs
        self.router._app = self
        self.init_app()

    def init_app(self):
        pass

    def wsgi(self, env, start_response):
        request = Request(env)
        response = self(request)
        body = response.start(request, start_response)
        return body

    def __call__(self, request):
        if not isinstance(request, Request):
            request = Request.from_request(request)
        result = self.router.match(request)
        if result:
            request, handle, method = result
            return handle(request)
        else:
            return self.error(request, 404)

    def set_middleware(self, middlewares):
        self.app.middlewares.extend(middlewares)

    def convert_fullurl(self, req, url):
        scheme = req.scheme
        hostname = req.host
        path = self.path
        if path[0] != "/":
            path = "/" + path
        if path[-1] == "/":
            path = path[0:-2]
        if url[0] != "/":
            url = "/" + url
        return scheme + "://" + hostname + path + url

    def convert_url(self, url):
        path = self.path
        if path[0] != "/":
            path = "/" + path
        if path[-1] == "/":
            path = path[0:-2]
        if url[0] != "/":
            url = "/" + url
        return path + url

    def revert_url(self, url):
        path = self.path
        if path[0] != "/":
            path = "/" + path
        if path[-1] == "/":
            path = path[0:-2]
        url = str(url)
        url = url[len(path) :]
        return url

    @property
    def view(self):
        toolkit = Path(os.path.dirname(__file__)) / "templates"
        self._view = Environment(
            loader=ChoiceLoader([
                FileSystemLoader(self.install_dir / self.template_dir),
                FileSystemLoader(toolkit),
            ])
        )

        def filter_user(arg):
            return [user for user in arg if user.__class__.__name__ == "User"]

        def filter_group(arg):
            return [group for group in arg if group.__class__.__name__ == "Group"]

        def markdown_(text):
            return Markup(markdown.markdown(text))

        self._view.filters["user"] = filter_user
        self._view.filters["group"] = filter_group
        self._view.filters["markdown"] = markdown_
        self._view.globals.update(
            url=self.convert_url,
            fullurl=self.convert_fullurl,
            dataurl=dataurl,
            uuid=uuid.uuid4
        )
        return self._view

    def error(self, request, code):
        template = self.view.get_template(str(code) + ".html")
        return Response.render(template, status=code)

    def match(self, request):
        result = self.router.match(request)
        if result == False:
            return False
        else:
            request, handle, method = result

            def _handle(request):
                request.app = self
                return handle(request)

            return request, _handle, method

    def save_params(self):
        self.params

    def uninstall(self):
        db = DatabaseManager()
        for model in self.models:
            model.__table__.drop(db.engine)

    def model(self, modelname):
        for model in self.models:
            if model.__class__.__name__ == modelname:
                return model

def _session_middleware():
    import base64

    from Crypto.Random import get_random_bytes

    from mitama.app import Middleware
    from mitama.app.http.session import EncryptedCookieStorage

    if "MITAMA_SESSION_KEY" in os.environ:
        session_key = os.environ["MITAMA_SESSION_KEY"]
    elif os.path.exists(".tmp/MITAMA_SESSION_KEY"):
        with open(".tmp/MITAMA_SESSION_KEY", "r") as f:
            session_key = f.read()
    else:
        key = get_random_bytes(16)
        session_key = base64.urlsafe_b64encode(key).decode("utf-8")
        if not os.path.exists(".tmp"):
            os.mkdir(".tmp")
        with open(".tmp/MITAMA_SESSION_KEY", "w") as f:
            f.write(session_key)

    class SessionMiddleware(Middleware):
        fernet_key = session_key

        def __init__(self):
            secret_key = base64.urlsafe_b64decode(self.fernet_key.encode("utf-8"))
            cookie_storage = EncryptedCookieStorage(secret_key)
            self.storage = cookie_storage

        def process(self, request, handler):
            request["mitama_session_storage"] = self.storage
            raise_response = False
            response = handler(request)
            if not isinstance(response, Response):
                return response
            session = request.get("mitama_session")
            if session is not None:
                if session._changed:
                    self.storage.save_session(request, response, session)
            if raise_response:
                raise response
            return response

    return SessionMiddleware

