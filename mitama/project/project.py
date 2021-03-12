import os
import sys
import importlib
import smtplib
import argparse
from traceback import print_exc
from pathlib import Path, PosixPath
from email.mime.text import MIMEText
from mitama.app.http import Request
from mitama.app import App, AppRegistry
from mitama.db import DatabaseManager

from . import commands


class Project(App):
    def __init__(
        self,
        *app_builders,
        port=80,
        password_validation=None,
        project_dir=Path(os.getcwd()),
        login_page="/login",
        mail={
            "host": "localhost",
            "port": 25,
            "address": "mitama@example.com"
        },
        vapid={
            "private_key": None,
            "public_key": None,
            "mailto": None
        },
        database={
            "type": "sqlite"
        },
        **kwargs
    ):
        if not isinstance(project_dir, PosixPath):
            project_dir = Path(project_dir)
        self.install_dir = Path(os.path.dirname(os.path.abspath(__file__)))
        self.project_dir = project_dir

        from mitama.models import User, Group, UserInvite, PushSubscription
        User._project = self
        Group._project = self
        UserInvite._project = self
        PushSubscription._project = self
        self.port = port
        self.mail = mail
        self.vapid = vapid
        self.password_validation = password_validation
        self.login_page = login_page
        self.apps = AppRegistry()
        self.apps.project = self
        for builder in app_builders:
            if builder.screen_name is None:
                builder.set_screen_name(builder.package)
            builder.set_project_dir(self.project_dir / builder.screen_name)
            app = builder.build()
            self.apps[app.screen_name] = app
        self.config = kwargs

        self.router = self.apps.router()

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

    @property
    def arg_parser(self):
        if not hasattr(self, "_arg_parser"):
            self._arg_parser = argparse.ArgumentParser(description="")
            subparser = self._arg_parser.add_subparsers()

            cmd_run = subparser.add_parser("run", help="Start serving project")
            cmd_run.add_argument(
                "-p",
                "--port",
                help="serving port",
                type=int,
                default=8080
            )
            cmd_run.set_defaults(handler=commands.run)
            cmd_auth = subparser.add_parser(
                "auth",
                help="Authenticate user identified by screen name and password"
            )
            cmd_auth.add_argument(
                "-u",
                "--user",
                help="user's screen name",
                type=str
            )
            cmd_auth.add_argument(
                "-p",
                "--password",
                help="password",
                type=str,
                nargs="?",
                default="",
                const=""
            )
            cmd_auth.set_defaults(handler=commands.auth)
            cmd_uninstall = subparser.add_parser(
                "uninstall",
                help="Uninstall app from project clearly"
            )
            cmd_uninstall.add_argument("app", help="app's screen name")
            cmd_uninstall.set_defaults(handler=commands.uninstall)
        return self._arg_parser

    def command(self):
        args = self.arg_parser.parse_args()
        if hasattr(args, 'handler'):
            try:
                DatabaseManager.start_session()
                args.handler(self, args)
            except Exception:
                DatabaseManager.rollback_session()
            finally:
                DatabaseManager.close_session()
        else:
            self.arg_parser.print_help()

    def uninstall(self, screen_name):
        self.apps[screen_name].uninstall()

    def app(self, appname):
        return self.apps[appname]

    def wsgi(self, env, start_response):
        try:
            DatabaseManager.start_session()
            body = super().wsgi(env, start_response)
        except Exception as err:
            print_exc(err)
            DatabaseManager.rollback_session()
            request = Request(env)
            body = self.error(request, 500).start(request, start_response)
        finally:
            DatabaseManager.close_session()
        return body


def include(
    package,
    screen_name=None,
    project_dir=None,
    project_root_dir=None,
    path=None
):
    if str(project_dir) not in sys.path:
        sys.path.append(str(project_dir))
    if package not in sys.modules:
        init = importlib.__import__(package, fromlist=["AppBuilder"])
    else:
        init = importlib.reload(package)
    builder = init.AppBuilder()
    if screen_name is None:
        screen_name = package
    builder.set_package(package)
    if screen_name is not None:
        builder.set_screen_name(screen_name)
    if project_root_dir is not None:
        builder.set_project_root_dir(project_root_dir)
    if project_dir is not None:
        builder.set_project_dir(project_dir)
    if path is not None:
        builder.set_path(path)
    return builder


