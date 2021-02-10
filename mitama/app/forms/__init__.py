from fields import Field
from errors import *

class Form:
    def __init__(self, data = {}):
        for key, value in data.items():
            if key in self.fields:
                self.fields[key].data = value
                self.fields[key].validate()

    def __getitem__(self, key):
        return self.fields[key].data

    @property
    def fields(self):
        ignored_attrs = ['fields']
        pairs = [
            (name, getattr(self, name))
            for name in dir(self)
            if name not in ignored_attrs and isinstance(getattr(self, name), Field)
        ]
        return dict(pairs)

    def reset(self):
        for key, value in data.items():
            if key in self.fields:
                self.fields[key].reset()
