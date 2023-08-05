import baseevent

HANDLER_PREFIX = "EVT_"

dispatcher = baseevent.Dispatcher()
post = dispatcher.post

class subscribe(object):
    """
    A decorator, which subscribes a callable to an event.
    Returns an instance which behaves like the original callable, with an extra unsubscribe method, which will unsubscribe the function.
    """
    def __init__(self, name):
        self.name = name

    def normal_call(self, *args, **kw):
        return self.func(*args, **kw)

    def __call__(self, func):
        self.func = func
        dispatcher.subscribe(func, self.name)
        self.__call__  = self.normal_call
        return self

    def subscribe(self, name):
        return subscribe(name)(self.func)

    def unsubscribe(self):
        """
        Unsubscribe this function from the event.
        """
        dispatcher.unsubscribe(self.func, self.name)


class Subscriber(object):
    """
    A Subscriber instance recieves multiple events, which are handled by methods defined with a special prefix, 'EVT_'.
    eg:

    class Handler(Subscriber):
        def EVT_SomeEvent(self, event):
            "This method will be called whenever 'SomeEvent' is posted."
            pass
        def EVT_SomeOtherEvent(self, event):
            "This method will be called whenever 'SomeOtherEvent' is posted."
            pass

    h = Handler()
    #enable event handling, call the .capture method.
    h.capture()
    #disable event handling, call the .release method.
    h.release()
    """

    def capture(self):
        """
        Enable event handling for all EVT_ methods in this instance.
        """
        self.__subscribers = []
        for meth in dir(self):
            if HANDLER_PREFIX in meth[:len(HANDLER_PREFIX)]:
                name = meth[len(HANDLER_PREFIX):]
                self.__subscribers.append(subscribe(name)(getattr(self, meth)))

    def release(self):
        """
        Disable event handling for all EVT_ methods in this instance.
        """
        for subscriber in self.__subscribers: subscriber.unsubscribe()




if __name__ == "__main__":
    class Test(Subscriber):
        def EVT_A(self, event, b=3):
            print event, event.args
            return 'xx'

    t = Test()
    t.capture()
    print post('A',b=1)
    t.release()
    print post('A',b=1)
    t.capture()
    print post('A',b=1)
    t.release()
    print post('A',b=1)
