"""

The nanothreads module simulates concurrency using Python generators to implement cooperative threads.

"""
__author__ = "simonwittber@gmail.com"

#import the best timing function possible (platform dependent)
import platform
if platform.system() == "Windows": from time import clock as time_func
else: from time import time as time_func
del platform

from collections import deque
from itertools import chain as chain_iterators
from threading import Thread, Lock
import time

import eventnet.driver

def throw(e):
    """
    Raise an exception. This function exists, so that lambda functions can raise Exceptions.
    """
    raise e

def synchronize(func):
    """
    A decorator which adds threading.Lock functionality around func.
    """
    lock = Lock()
    def f(*args, **kw):
        lock.acquire()
        try:
            r = func(*args, **kw)
        finally:
            lock.release()
        return r
    return f


class _KillFibra(Exception): pass


class NanoEvent(object): pass


class UNBLOCK(NanoEvent):
    """
    Yield UNBLOCK() to spawn the next iteration into a seperate, OS level thread.
    """
    pass


class CONTINUE(NanoEvent):
    """
    Yield CONTINUE() or None, to allow the next task in the schedule to iterate.
    """
    pass

class RESUME_ON_EVENT(NanoEvent):
    """
    Yield RESUME_ON_EVENT(event_name) to pause the task, and resume when event_name is posted.
    """
    def __init__(self, name):
        self.name = name

class Fibra(object):
    """
    Fibra is a Latin word, meaning fiber. Fibra instances are very light cooperatives threads, which are iterated by the Pool.
    To create a Fibra instance, pass a generator function the the Pool().register method, which will return a Fibra instance.
    A Fibra instance can .preempt, be .pause(d), .resume(d), .kill(ed), and .end(ed).
    When a Fibra instance ends, it calls all functions which were registered with the Fibra.call_on_exit method.
    When a Fibra instance is killed, it does not call any exit functions.
    """
    __slots__ = ['__task','__pool','next','_state','_thread']
    def __init__(self, task, pool):
        self.__task = task
        self.__pool = pool
        self.next = self.__task.next
        self._state = deque()

    def __repr__(self):
        return "<%s object at 0x%X state:%s>" % (self.__class__.__name__, id(self), self.state)

    def get_state(self):
        return self._state[0]
    state = property(fget=get_state)

    def pause(self):
        """
        Stops the execution of the fibra, until the resume method is called.
        """
        self._state.appendleft('PAUSED')
        self.next = lambda: None

    def resume(self):
        """
        Resumes the fibra after it has been paused.
        """
        if self.state == 'PAUSED':
            self._state.popleft()
            self.next = self.__task.next
        else:
            raise RuntimeError, 'Cannot resume a %s Fibra.' % self.state

    def kill(self):
        """
        Stop the fibra, and do not call any registered exit functions.
        """
        self._state.appendleft('DEAD')
        self.next = lambda: throw(_KillFibra)

    def end(self):
        """
        Stop the fibra, and call any registered exit functions.
        """
        self._state.appendleft('DEAD')
        self.next = lambda: throw(StopIteration)

    def call_on_exit(self, func, *args, **kw):
        """
        Add a function which is called when the fibra terminates.
        """
        self.__pool.exit_funcs[self].append((func, list(args), dict(kw)))

    def preempt(self):
        """
        Preempt the schedule of the Fibra, moving it to the top of the execution pool.
        """
        self.__pool.preempt(self)

    def spawn_thread(self):
        """
        Run the next iteration step of the task in a seperate thread.
        """
        self._state.appendleft('THREADING')

        def yield_one_step():
            try:
                self.__task.next()
            except Exception, e:
                self.next = lambda: throw(e)
            def resume():
                self._thread.join()
                self.__pool._remove_wait()
                self.__pool.pool.append(self)
                self._state.popleft()
                yield None
            self.__pool.register(resume)

        self._thread = Thread(target=yield_one_step)
        self._thread.start()

class Pool(object):
    """
    A Cooperative/Preemptive thread scheduler, implemented using generators.
    """
    __slots__ = ["pool","exit_funcs","wait_count","lock"]
    def __init__(self):
        self.pool = deque()
        self.exit_funcs = {}
        self.wait_count = 0
        self.lock = Lock()

    @synchronize
    def _add_wait(self):
        self.wait_count += 1

    @synchronize
    def _remove_wait(self):
        self.wait_count -= 1

    @synchronize
    def register(self, func, *args, **kw):
        """
        Add a new generator (task) to the pool. Returns a fibra instance, which can control the task.
        """
        gen = func(*args, **kw)
        fibra = Fibra(gen, self)
        self.pool.append(fibra)
        self.exit_funcs[fibra] = []
        return fibra

    def preempt(self, fibra):
        """
        Preempt a task, moving it to the top of the execution queue.
        """
        for index, match in enumerate(self.pool):
            if fibra == match:
                self.pool.rotate(-index)
                item = self.pool.popleft()
                self.pool.rotate(index)
                self.pool.appendleft(item)
                return

    def defer(self, func, *args, **kw):
        """
        Defer a function call until the next iteration of the pool.
        """
        def deferred(*args, **kw):
            func(*args, **kw)
            yield None
        return self.register(deferred, *args, **kw)

    def defer_for(self, seconds, func, *args, **kw):
        """
        Defer a function call for a number of seconds.
        """
        def deferred(seconds, func, *args, **kw):
            start = time_func()
            while (time_func() - start) <= seconds: yield None
            func(*args, **kw)
        return self.register(deferred, seconds, func, *args, **kw)

    def call_exit_funcs(self, task):
        """
        Call all exit functions which are registered for a task.
        """
        for ef in self.exit_funcs[task]: ef[0](*ef[1],**ef[2])

    def __iter__(self):
        """
        Iteratie the execution queue. Used for integrating nanothreads with other mainloop constructs.
        """
        #This is a cut and paste of the loop function, with an extra yield statement.
        #This is usually bad practice, however, I've done it here for performance reasons. NanoThreads needs to be fast.
        self_call_exit_funcs = self.call_exit_funcs
        self_pool_popleft = self.pool.popleft
        self_pool_append = self.pool.append
        self_pool = self.pool
        while len(self_pool)  or (self.wait_count > 0):
            try:
                while len(self_pool) > 0:
                    task = self_pool_popleft()
                    r = task.next()
                    if  isinstance(r, UNBLOCK):
                        self._add_wait()
                        task.spawn_thread()
                    elif isinstance(r, RESUME_ON_EVENT):
                        self._add_wait()
                        task._state.appendleft('WAITING')
                        self._resume_on_event(r.name, task)
                    else:
                        self_pool_append(task)
                    yield None
            except StopIteration:
                task._state.appendleft('DEAD')
                self_call_exit_funcs(task)
            except _KillFibra:
                task._state.appendleft('DEAD')
            yield None

    def shutdown(self):
        """
        Shutdown the looping scheduler cleanly.
        """
        for task in self.pool: task.end()

    def loop(self):
        """
        Start the scheduler, and keep running until all tasks have finished.
        """
        #The below assignments are simple optimisations, which help avoid multiple attribute lookups per loop.
        self_call_exit_funcs = self.call_exit_funcs
        self_pool_popleft = self.pool.popleft
        self_pool_append = self.pool.append
        self_pool = self.pool
        while len(self_pool)  or (self.wait_count > 0):
            try:
                while len(self_pool) > 0:
                    task = self_pool_popleft()
                    r = task.next()
                    if  isinstance(r, UNBLOCK):
                        self._add_wait()
                        task.spawn_thread()
                    elif isinstance(r, RESUME_ON_EVENT):
                        self._add_wait()
                        task._state.appendleft('WAITING')
                        self._resume_on_event(r.name, task)
                    else:
                        self_pool_append(task)
            except StopIteration:
                task._state.appendleft('DEAD')
                self_call_exit_funcs(task)
            except _KillFibra:
                task._state.appendleft('DEAD')

    def _resume_on_event(self, event_name, task):
        @eventnet.driver.subscribe(event_name)
        def resume_task(event):
            self.pool.append(task)
            resume_task.kill()
            self._remove_wait()
            task._state.popleft()

    def chain(self, *args):
        """
        Chain the execution of multiple, simple generators.
        """
        iterators = [i() for i in args]
        return self.register(chain_iterators, *iterators)




#generate globals for the user.
__pool = Pool()

for name in dir(__pool):
    if name[:2] != "__":
        attr = getattr(__pool, name)
        if callable(attr):
            globals()[name] = attr
