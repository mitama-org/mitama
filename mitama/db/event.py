class Event:
    def __init__(self, doc=None):
        self.__doc__ = doc

    def __get__(self, obj, objtype=None):
        if obj is None:
            return Self
        return EventHandler(self, obj)

    def __set__(self, obj, objtype=None):
        pass

class EventHandler:
    def __init__(self, event, obj):
        self.event = event
        self.obj = obj
    def _getfunctionlist(self):
        try:
            eventhandler = self.obj.__eventhandler__
        except AttributeError:
            eventhandler = self.obj.__eventhandler__ = {}
        return eventhandler.setdefault(self.event, [])
    def __iadd__(self, func):
        self._getfunctionlist().append(func)
        return self
    def __isub__(self, func):
        self._getfunctionlist().remove(func)
        return self
    def __call__(self,earg=None):
        for func in self._getfunctionlist():
            func(self.obj, earg)

