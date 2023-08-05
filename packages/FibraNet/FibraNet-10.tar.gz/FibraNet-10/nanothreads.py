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

The nanothreads module simulates concurrency using Python generators to 
implement cooperative threads.

"""

__author__ = "simonwittber@gmail.com"

#import the best timing function possible (platform dependent)
import platform
if platform.system() == "Windows": 
    from time import clock as time_func
else: 
    from time import time as time_func
del platform

from collections import deque
from itertools import chain as chain_iterators
from threading import Thread, Lock
import time

import eventnet.driver


#core functions and classes

def throw(e):
    """
    Raise an exception. This function exists, so that lambda functions can 
    raise Exceptions.
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
    Yield UNBLOCK() to spawn the next iteration into a seperate, OS level 
    thread.
    """
    pass


class CONTINUE(NanoEvent):
    """
    Yield CONTINUE() or None, to allow the next task in the schedule to 
    iterate.
    """
    pass


class SLEEP(NanoEvent):
    """
    Yield SLEEP() to make the task pause iterations for a period.
    """
    def __init__(self, seconds):
        self.seconds = seconds


class RESUME_ON_EVENT(NanoEvent):
    """
    Yield RESUME_ON_EVENT(event_name) to pause the task, and resume when 
    event_name is posted.
    """
    def __init__(self, name):
        self.name = name


class Fibra(object):
    """
    Fibra is a Latin word, meaning fiber. Fibra instances are very light 
    cooperatives threads, which are iterated by the Pool.
    To create a Fibra instance, pass a generator function the the Pool().
    register method, which will return a Fibra instance.
    A Fibra instance can be .pause(d), .resume(d), .kill(ed), and .end(ed).
    When a Fibra instance ends, it calls all functions which were registered 
    with the Fibra.call_on_exit method.
    When a Fibra instance is killed, it does not call any exit functions.
    """
    __slots__ = 'task', 'next', 'thread', 'exit_funcs'
    
    def __init__(self, task):
        self.task = task
        try:
            self.next = self.task.next
        except AttributeError, e:
            raise AttributeError("Cannot install a function as a nanothread, use a generator function.")
            
        self.exit_funcs = []

    def __repr__(self):
        return "<%s object at 0x%X >" % (self.__class__.__name__, id(self))

    def pause(self):
        """
        Stops the execution of the fibra, until the resume method is called.
        """
        self.next = lambda: None

    def resume(self):
        """
        Resumes the fibra after it has been paused.
        """
        self.next = self.task.next
        
    def kill(self):
        """
        Stop the fibra, and do not call any registered exit functions.
        """
        self.next = lambda: throw(_KillFibra)

    def end(self):
        """
        Stop the fibra, and call any registered exit functions.
        """
        self.next = lambda: throw(StopIteration)

    def call_on_exit(self, func, *args, **kw):
        """
        Add a function which is called when the fibra terminates.
        """
        self.exit_funcs.append((func, list(args), dict(kw)))
        
    def call_exit_funcs(self):
        """
        Calls exit functions registered for this instance. This method is 
        called automatically by the scheduler when the task finishes.
        """
        for func, arg, kw in self.exit_funcs:
            func(*arg, **kw)

    def spawn_thread(self, onThreadFinish):
        """
        Run the next iteration step of the task in a seperate thread.
        """
        def yield_one_step():
            try:
                self.task.next()
            except Exception, e:
                self.next = lambda: throw(e)
            onThreadFinish(self)

        self.thread = Thread(target=yield_one_step)
        self.thread.start()
        

class Pool(object):
    """
    A Cooperative/Preemptive thread scheduler, implemented using generators.
    """
    __slots__ = ["pool", "running"]
    def __init__(self):
        self.pool = deque()
        self.running = False

    @synchronize
    def install(self, generator):
        """
        Add a new generator (task) to the pool. Returns a fibra instance, 
        which can control the task.
        """
        fibra = Fibra(generator)
        self.pool.append(fibra)
        return fibra
        
    @synchronize
    def install_fibra(self, fibra):
        """
        Add a fibra to the pool. Returns the same Fibra.
        """
        self.pool.append(fibra)
        return fibra
        
    def chain(self, *args):
        """
        Chain the execution of multiple generators.
        """
        return self.install(chain_iterators(*args))

    def defer(self, func, *args, **kw):
        """
        Defer a function call until the next iteration of the pool.
        """
        def deferred(*args, **kw):
            func(*args, **kw)
            yield None
            
        return self.install(deferred(*args, **kw))

    def defer_for(self, seconds, func, *args, **kw):
        """
        Defer a function call for a number of seconds.
        """
        def deferred(seconds, func, *args, **kw):
            start = time_func()
            while (time_func() - start) <= seconds: 
                yield None
            func(*args, **kw)
            yield None
            
        return self.install(deferred(seconds, func, *args, **kw))
        
    def poll(self):
        """
        Iterate the execution queue. Used for integrating nanothreads with 
        other mainloop constructs.
        """
        try:
            task = self.pool.popleft()
        except IndexError:
            return
        try:
            r = task.next()
        except StopIteration:
            task.call_exit_funcs()
            return
        except _KillFibra:
            return
        if  isinstance(r, UNBLOCK):
            task.spawn_thread(self.resume_from_thread)
        elif isinstance(r, RESUME_ON_EVENT):
            self.resume_on_event(r.name, task)
        elif isinstance(r, SLEEP):
            self.resume_later(r.seconds, task)
        else:
            self.pool.append(task)

    def loop(self):
        """
        Start the scheduler, and keep running until all tasks have finished.
        """
        #The below assignments are simple optimisations, which help avoid multiple attribute lookups per loop.
        self_pool_popleft = self.pool.popleft
        self_pool_append = self.pool.append
        self_pool = self.pool
        self.running = True
        while self.running:
            try:
                task = self_pool_popleft()
            except IndexError:
                continue
            try:
                r = task.next()
            except StopIteration:
                task.call_exit_funcs()
                continue
            except _KillFibra:
                continue
            if  isinstance(r, UNBLOCK):
                task.spawn_thread(self.resume_from_thread)
            elif isinstance(r, RESUME_ON_EVENT):
                self.resume_on_event(r.name, task)
            elif isinstance(r, SLEEP):
                self.resume_later(r.seconds, task)
            else:
                self_pool_append(task)
                
    def shutdown(self):
        """
        Shutdown the looping scheduler cleanly.
        """
        self.running = False
    
    def resume_later(self, seconds, task):
        def resume_task():
            self.pool.append(task)
        self.defer_for(seconds, resume_task)

    def resume_on_event(self, event_name, task):
        @eventnet.driver.subscribe(event_name)
        def resume_task():
            self.pool.append(task)
            resume_task.release()
            
    def resume_from_thread(self, fibra):
        def reinstall():
            fibra.thread.join()
            self.pool.append(fibra)
        self.defer(reinstall)


# This code generates global names which point to method names of a global 
# Pool instance. This is so the user can use these names to access a default
# global nanothread scheduler.

__pool = Pool()
pool = __pool.pool
for name in dir(__pool):
    if name[:2] != "__":
        attr = getattr(__pool, name)
        if callable(attr):
            globals()[name] = attr


#user functions and classes
        
class TaskQueue(object):
    def __init__(self):
        self.tasks = []
        self.current_thread = None
        
    def _update(self):
        if len(self.tasks) > 0 and self.current_thread is None:
            self.current_thread = install(self.tasks.pop(0))
            self.current_thread.call_on_exit(self._finish_task)
    
    def _finish_task(self):
        self.current_thread = None
        self._update()
        
    def install(self, task):
        self.tasks.append(task)
        self._update()
        
    def flush(self):
        self.tasks[:] = []
        if hasattr(self, 'current_thread'):
            self.current_thread.kill()
        self.current_thread = None
        