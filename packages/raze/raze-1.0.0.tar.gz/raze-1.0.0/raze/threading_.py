"""
RAZE Python Libraries
Extensions to the standard threading library.


$Id: threading_.py 256 2006-05-31 04:36:35Z james $
Copyright (c) 2006 James Harris
"""
__revision__ = "$Revision: 256 $"
__location__ = "$URL: http://localhost/svn/raze/tags/raze-1.0.0/raze/threading_.py $"
__all__ = [ 'SimpleCondition' ]

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


def _test():
    """ Test this module. """
    import doctest
    import threading_
    return doctest.testmod(threading_)
