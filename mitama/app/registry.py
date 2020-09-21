from mitama.extra import _Singleton

class AppRegistry(_Singleton):
    apps = list()
    def append(self, app):
        self.apps.append(app)
    def __iter__(self):
        for app in self.apps:
            yield app
