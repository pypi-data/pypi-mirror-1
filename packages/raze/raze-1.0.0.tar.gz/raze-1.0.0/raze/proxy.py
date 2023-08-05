"""
RAZE Python Libraries
Basic proxy object.


    >>> class Foo(object):
    ...   def doit(self):
    ...     print 'I did it!'

    >>> f = Foo()
    >>> p = Proxy(f)
    >>> p.doit()
    I did it!

    >>> p.foobar = 2
    >>> f.foobar
    2

    >>> f.spam = 3
    >>> p.spam
    3

    >>> del p.spam
    >>> hasattr(f, 'spam')
    False


$Id: proxy.py 256 2006-05-31 04:36:35Z james $
Copyright (c) 2006 James Harris
"""
__revision__ = "$Revision: 256 $"
__location__ = "$URL: http://localhost/svn/raze/tags/raze-1.0.0/raze/proxy.py $"
__all__ = [ 'Proxy' ]

from weakref import WeakKeyDictionary


# store objects external to class so that there are no instance/class
# attribute naming collisions
_proxy_objects = WeakKeyDictionary()

class Proxy(object):
    """ Basic proxy wrapper. """    
    def __init__(self, obj):
        _proxy_objects[self] = obj

    def __getattribute__(self, name):
        return getattr(_proxy_objects[self], name)
    
    def __setattr__(self, name, value):
        return setattr(_proxy_objects[self], name, value)

    def __delattr__(self, name):
        return delattr(_proxy_objects[self], name)


def _test():
    """ Test this module. """
    import doctest
    import proxy
    return doctest.testmod(proxy)
