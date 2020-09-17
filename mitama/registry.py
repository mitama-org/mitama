from mitama.extra import _Singleton

class Registry(_Singleton):
    def __init__(self):
        self.data = dict()
    def __setitem__(self, k, v):
        self.data[k] = v
    def __getitem__(self, k):
        return self.data[k]
    def __delitem__(self, k):
        del self.data[k]
