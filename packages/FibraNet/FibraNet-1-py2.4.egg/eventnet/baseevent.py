debug = False

class Event(object):
    def __init__(self, name, **kw):
        self.__dict__.update(kw)
        self.args = kw
        self.name = name

class Dispatcher(object):
    """
    A simple event dispatcher.
    """
    def __init__(self):
        self.events = {}

    def subscribe(self, func, name):
        """
        Subscribe a callable to an event.
        """
        try:
            self.events[name].append(func)
        except KeyError:
            self.events[name] = [func]

    def unsubscribe(self, func, name):
        """
        Unsubscribe a callable from an event.
        """
        self.events[name].remove(func)

    def post(self, name, **kw):
        """
        Post an event, which is dispatched to all callables which are subscribed to that event.
        """
        if debug:
            print 'EVENTNET:', name, kw
        try:
            event = Event(name, **kw)
            results = tuple(i(event) for i in self.events[name])
        except KeyError:
            results = tuple()
        return results


