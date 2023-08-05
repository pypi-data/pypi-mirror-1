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

A simple event/signal dispatcher.

"""

import weakref
from collections import deque


def call_with_keywords(func, *args, **kw):
    """
    Call a function with allowed keywords only.
    """
    return func(*args, **dict([i for i in kw.items() if i[0] in func.func_code.co_varnames]))


class Dispatcher(object):
    """
    A simple event dispatcher.
    """
    def __init__(self):
        self.events = {}
        self.stacks = {}
        
    def subscribe(self, func, name, static=False):
        """
        Subscribe a callable to an event. Keeps a weakref to func.
        """
        
        if static:
            print func
            callable = func.im_func
            obj = func
            function = lambda kw: call_with_keywords(callable, obj, **kw)
        else:
            if hasattr(func, 'im_self'):
                obj = weakref.proxy(func.im_self)
                callable = func.im_func
                function = lambda kw: call_with_keywords(callable, obj, **kw)
                function.ref = weakref.ref(func.im_self, lambda x: self.events[name].remove(function))
            else:
                callable = weakref.proxy(func)
                function = lambda kw: call_with_keywords(callable, **kw)
                function.ref = weakref.ref(func, lambda x: self.events[name].remove(function))
                    
        try:
            self.events[name].append(function)
        except KeyError:
            self.events[name] = [function]
        except AttributeError:
            raise RuntimeError("Cannot subscribe to a captured event. %s is currently captured by %s." % (name,self.events[name][0]))
        
        return function    
            
    def capture(self, func, name):
        """
        Bind a callable exclusively to an event.
        """
        try:
            handlers = self.events[name]
        except KeyError:
            handlers = []
        self.stacks.setdefault(name, deque()).appendleft(handlers)
        function = lambda kw: call_with_keywords(func, **kw)
        self.events[name] = (function,)
        return function
        
    def release(self, func, name):
        """
        Release a captured event.
        """
        if func is not self.events[name][0]:
            raise RuntimeError("A callable bound to %s was released out of sequence." % name)
        handlers = self.stacks[name].popleft()
        self.events[name] = handlers
        
    def unsubscribe(self, func, name):
        """
        Unsubscribe a callable from an event.
        """
        try:
            self.events[name].remove(func)
        except ValueError:
            pass
        
    def post(self, _event_identity, **kw):
        """
        Post an event, which is dispatched to all callables which are subscribed to that event.
        """
        try:
            events = self.events[_event_identity]
        except KeyError:
            return tuple()
        else:
            return tuple((i(kw) for i in events))
        


