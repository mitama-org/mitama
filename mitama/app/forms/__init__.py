from .fields import *
from .errors import *
from mitama._extra import deepupdate

class Form:
    def __new__(cls, data=None):
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

    def __init__(self, data=None):
        for field in self.fields.values():
            if isinstance(field, DictFieldInstance):
                field.data = {}
                for k in data.keys():
                    if '.' in k:
                        k_ = k.split('.')
                        name = k_.pop(0)
                        last_key = '.'.join(k_[(field.depth-1):])
                        data_ = {}
                        if name == field.name:
                            if field.listed:
                                data_[last_key] = data.getlist(k)
                            else:
                                data_[last_key] = data.get(k)
                            if field.depth > 1:
                                for k__ in k_[:(field.depth-1)]:
                                    data_ = {
                                        k__: data_
                                    }
                            deepupdate(field.data, data_)
            elif field.listed:
                field.data = data.getlist(field.name)
            elif field.name in data:
                field.data = data.get(field.name)
            field.validate()

    def __getitem__(self, key):
        return self.fields[key].data

    def reset(self):
        for value in self.fields.values():
            value.reset()
