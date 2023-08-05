import weakref

class WeakMethodProxy(object):
    def __init__(self, bound_method, *args, **kw):
        self.func = bound_method.im_func
        self.ref = weakref.ref(bound_method.im_self, *args, **kw)
        
    def __call__(self, *args, **kw):
        ref = self.ref()
        if ref is None: raise ReferenceError
        return self.func(ref, *args, **kw)
        

def proxy(callable, *args, **kw):
        if hasattr(callable, 'im_self'):
            return WeakMethodProxy(callable, *args, **kw)
        return weakref.proxy(callable, *args, **kw)
    