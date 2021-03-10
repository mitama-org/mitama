class EventManager:
    def __init__(self, events=[], doc=None):
        self.__doc__ = doc
        self.events = {}
        for event in events:
            self.events[event] = Event()

    def __get__(self, obj, objtype=None):
        if obj is None:
            return self
        return EventManagerInstance(self, obj)

    def __set__(self, obj, objtype=None):
        pass

    def __getitem__(self, key):
        return self.events[key]

    def __setitem__(self, key, value):
        self.events[key] = value

    def listen(self, event):
        self.events[event] = Event()


class EventManagerInstance:
    def __init__(self, event_manager, obj):
        self.event_manager = event_manager
        self.object = obj

    def __getitem__(self, key):
        return self.event_manager.events[key].handler(self.object)


class Event:
    def __init__(self):
        self._funcs = []

    def __iadd__(self, func):
        self._funcs.append(func)
        return self

    def __isub__(self, func):
        self._funcs.remove(func)
        return self

    def handler(self, obj):
        return EventHandler(self, obj)


class EventHandler:
    def __init__(self, event, obj):
        self.event = event
        self.object = obj

    def __call__(self, **kwargs):
        for f in self.event._funcs:
            f(self.object, **kwargs)
