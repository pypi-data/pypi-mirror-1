"""

A simple event/signal dispatcher.

"""

def call_with_keywords(func, kw):
    """
    Call a function with allowed keywords only.
    """
    return func(**dict([i for i in kw.items() if i[0] in func.func_code.co_varnames]))


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

    def post(self, _event_identity, **kw):
        """
        Post an event, which is dispatched to all callables which are subscribed to that event.
        """
        if _event_identity in self.events:
            return tuple(call_with_keywords(i, kw) for i in self.events[_event_identity])
        else:
            return tuple()


