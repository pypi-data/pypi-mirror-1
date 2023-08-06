
class Event(object):
    def __init__(self):
        self._handlers = []

    def __iadd__(self, other):
        self._handlers.append(other)
        return self

    def __call__(self, sender, args):
        result = None
        for handler in self._handlers:
            result = handler(sender, args)
        return result