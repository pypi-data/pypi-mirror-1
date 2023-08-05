"""
RAZE Python Libraries
Extensions to the standard threading library.


RAZE - Copyright (c) 2006 James Harris, Erin Houston
$Id: threading_.py 258 2006-11-23 01:40:07Z james $
"""
__revision__ = "$Revision: 258 $"
__location__ = "$URL: http://icecave.svn.net.au/dav/lib/raze/tags/raze-1.1.0/raze/threading_.py $"
__all__ = [ 'SimpleCondition', 'exclusive' ]

try:
    from threading import *
    import threading as threading_lib
except ImportError:
    from dummy_threading import *
    import dummy_threading as threading_lib

__all__ += threading_lib.__all__


class SimpleCondition(object):
    """ Provides a simpler atomic interface to a Condition object. """
    __slots__ = ('condition')

    def __init__(self, condition=None):
        self.condition = condition or Condition()
    
    def wait(self, timeout=None):
        """ Acquire the condition, wait for a notify then release. """
        self.condition.acquire()
        try:
            self.condition.wait(timeout)
        finally:
            self.condition.release()
    
    def notify(self):
        """ Acquire the condition, notify a waiting thread then release. """
        self.condition.acquire()
        try:
            self.condition.notify()
        finally:
            self.condition.release()

    def notify_all(self):
        """ Acquire the condition, notify all waiting thread then release. """
        self.condition.acquire()
        try:
            self.condition.notifyAll()
        finally:
            self.condition.release()


def exclusive(method):
    """ Decorator that locks a mutex around calls. """
    mutex = RLock()
    def invoker(*pos, **kw):
        try:
            mutex.acquire()
            return method(*pos, **kw)
        finally:
            mutex.release()
    invoker.__name__ = method.__name__
    return invoker


def _test():
    """ Test this module. """
    import doctest
    import threading_
    return doctest.testmod(threading_)
