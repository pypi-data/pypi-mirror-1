#Copyright (c) 2006 Simon Wittber
#
#Permission is hereby granted, free of charge, to any person
#obtaining a copy of this software and associated documentation files
#(the "Software"), to deal in the Software without restriction,
#including without limitation the rights to use, copy, modify, merge,
#publish, distribute, sublicense, and/or sell copies of the Software,
#and to permit persons to whom the Software is furnished to do so,
#subject to the following conditions:
#
#The above copyright notice and this permission notice shall be
#included in all copies or substantial portions of the Software.
#
#THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
#EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
#MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
#NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS
#BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN
#ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
#CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
#SOFTWARE.

"""

This module contains helpers for using the basevent.Dispatcher.
It provides a decorator for subscribing functions and methods, a class for
handling mutiple events and a hook function for Dispatcher.post integration.

"""
import weakref
import threading
import baseevent
import nanothreads

SUBSCRIBE_PREFIX = "EVT_"
CAPTURE_PREFIX = "CAP_"

dispatcher = baseevent.Dispatcher()

post_lock = threading.Lock()
def _post(*args, **kw):
    post_lock.acquire() 
    try:
        return dispatcher.post(*args, **kw)
    finally:
        post_lock.release()
        
def post(*args, **kw):
    nanothreads.defer(_post, *args, **kw)

def hook(callback):
    """
    Hook a callback function into the event dispatch machinery.
    """
    first_post = globals()["post"]
    def hooked_post(name, **kw):
        callback(name, **kw)
        return first_post(name, **kw)
    globals()["post"] = hooked_post
    

class subscribe(object):
    """
    A decorator, which subscribes a callable to an event.
    """
    def __init__(self, _event_identity, **kw):
        self.name = _event_identity
        self.kw = kw
    
    def __call__(self, func):
        self.func = func
        self.id = dispatcher.subscribe(func, self.name, **self.kw)
        return self
    
    def release(self):
        """
        Unsubscribe this function from the event.
        """
        dispatcher.unsubscribe(self.id, self.name)


class capture(object):
    """
    A decorator, which binds a callable to an event.
    """
    def __init__(self, _event_identity):
        self.name = _event_identity

    
    def __call__(self, func):
        self.id = dispatcher.capture(func, self.name)
        return self
    
    def release(self):
        """
        Unbind this function from the event.
        """
        dispatcher.release(self.id, self.name)


class Subscriber(object):
    """
    This is a mixin class. It has no __init__ constructor.
    
    A Subscriber instance receives multiple events, which are handled by 
    methods defined with a special prefix, 'EVT_'.
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
            if SUBSCRIBE_PREFIX in meth[:len(SUBSCRIBE_PREFIX)]:
                name = meth[len(SUBSCRIBE_PREFIX):]
                s = subscribe(name)(getattr(self, meth))
                self.__subscribers.append(s)
            if CAPTURE_PREFIX in meth[:len(CAPTURE_PREFIX)]:
                name = meth[len(CAPTURE_PREFIX):]
                s = capture(name)(getattr(self, meth))
                self.__subscribers.append(s)

    def release(self):
        """
        Disable event handling for all EVT_ methods in this instance.
        """
        for subscriber in self.__subscribers: subscriber.release()


class Handler(object):
    """
    A handler is different, in that it does not receive dispatched events, 
    but only events which are posted directly to it, via its own post method.
    """
    def post(self, _event_identity, **kw):
        return tuple([baseevent.call_with_keywords(getattr(self, meth), **kw) for meth in dir(self) if SUBSCRIBE_PREFIX+_event_identity == meth])
        


