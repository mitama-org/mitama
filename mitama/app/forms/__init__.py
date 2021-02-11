from .fields import *
from .errors import *

class Form:
    def __new__(cls, data = None):
        self = object.__new__(cls)
        ignored_attrs = ['fields']
        pairs = [
            (name, getattr(self, name).instance())
            for name in dir(self)
            if name not in ignored_attrs and isinstance(getattr(self, name), Field)
        ]
        self.fields = dict(pairs)
        for key in self.fields.keys():
            if self.fields[key].name == None:
                self.fields[key].name = key
        return self

    def __init__(self, data = None):
        for field in self.fields.values():
            if field.name in data:
                field.data = data[field.name]
            field.validate()

    def __getitem__(self, key):
        return self.fields[key].data

    def reset(self):
        for value in self.fields.values():
            value.reset()
