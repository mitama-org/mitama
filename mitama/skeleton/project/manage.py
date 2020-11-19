from mitama.app import _MainApp, AppRegistry
from mitama.http import run_app
import sys

app_registry = AppRegistry()
app_registry.load_config()
app = _MainApp(app_registry)
