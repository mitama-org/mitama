import os
import sys
import importlib
from mitama.app import AppRegistry
from mitama.app.http import run_app
from getpass import getpass


def run(project, args):
    port = args.port
    project.port = port
    run_app(project, project.port)

def auth(project, args):
    from mitama.models import User
    user = args.user
    password = args.password
    if password == "":
        password = getpass("Password:")
    try:
        user = User.password_auth(user, password)
        print(user.get_jwt())
        sys.exit(0)
    except Exception:
        print("Authentication failed")
        sys.exit(1)

def uninstall(project, args):
    project.uninstall(args.app)
