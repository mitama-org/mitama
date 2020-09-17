import inspect
import os

class Builder(object):
    app = None
    def __init__(self):
        self.data = {}
        pass
    def set_path(self, path):
        self.data['path'] = path
    def set_name(self, name):
        self.data['name'] = name
    def set_project_dir(self, path):
        self.data['project_dir'] = path
    def build(self):
        install_dir = os.path.dirname(inspect.getfile(self.__class__))
        self.data['install_dir'] = install_dir
        return self.app(**self.data)
