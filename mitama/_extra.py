
class _Singleton:
    _instance = None
    def __new__(cls, *args, **kwargs):
        if cls._instance == None:
            cls._instance = super(_Singleton, cls).__new__(cls)
        return cls._instance


class _classproperty:
    def __init__(self, fget = None, doc = None):
        self.fget = fget
        self.__doc__ = self.fget.__doc__ if doc == None else doc
    def __get__(self, obj, cls=None):
        if cls is None:
            cls = type(obj)
        return self.fget(cls)

