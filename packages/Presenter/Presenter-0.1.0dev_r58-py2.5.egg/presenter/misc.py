from collections import defaultdict

class DeclarativeMeta(type):
    def __new__(meta, class_name, bases, new_attrs):
        cls = type.__new__(meta, class_name, bases, new_attrs)
        cls.__classinit__.im_func(cls, new_attrs)
        return cls

class EventHandler(object):
    def __init__(self, *args, **kwargs):
        super(EventHandler, self).__init__(*args, **kwargs)
        self._handlers = defaultdict(list)

    def emit(self, signal, *args, **kwargs):
        for fn in self._handlers[signal]:
            fn(*args, **kwargs)

    def connect(self, signal, function):
        self._handlers[signal].append(function)

