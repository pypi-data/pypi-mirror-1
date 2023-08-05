"""
RAZE Python Libraries
Utilities for finding the first available item in a given namespace or sequence.


The CoalesceAttributes class allows cascaded access of attributes on a
sequence of namespaces.

    >>> class Foo(object):
    ...   one = 'foo1'
    ...   two = 'foo2'

    >>> class Bar(object):
    ...   one = 'bar1'
    ...   three = 'bar3'

    >>> ca = CoalesceAttributes(Bar, Foo)
    >>> ca.one
    'bar1'

    >>> ca.two
    'foo2'
    
    >>> ca.three
    'bar3'

    >>> del ca.one
    >>> ca.one
    'foo1'

    >>> ca.new = 'new'
    >>> ca.new is Bar.new
    True

    >>> ca.not_found
    Traceback (most recent call last):
    AttributeError: not_found


The coalesce function returns the first of its arguments that is not None.
None is returned only if all arguments are None or no arguments are provided.

    >>> coalesce(None, None, 46, 2) == 46
    True

    >>> coalesce(None, None) is None
    True

    >>> coalesce() is None
    True


RAZE - Copyright (c) 2006 James Harris, Erin Houston
$Id: coalesce.py 258 2006-11-23 01:40:07Z james $
"""
__revision__ = "$Revision: 258 $"
__location__ = "$URL: http://icecave.svn.net.au/dav/lib/raze/tags/raze-1.1.0/raze/coalesce.py $"
__all__ = [ 'CoalesceAttributes', 'coalesce' ]


class CoalesceAttributes(object):
    """ Perform cascading attribute access on a sequence of namespaces. """
    def __init__(self, *namespaces):
        object.__setattr__(self, '_namespaces', namespaces)

    def __getattr__(self, name):
        for ns in self._namespaces:
            try:
                return getattr(ns, name)
            except AttributeError:
                pass
        raise AttributeError(name)

    def __setattr__(self, name, value):
        try:
            ns = self._namespaces[0]
            return setattr(ns, name, value)
        except IndexError:
            raise AttributeError(name)

    def __delattr__(self, name):
        for ns in self._namespaces:
            try:
                return delattr(ns, name)
            except AttributeError:
                pass
        raise AttributeError(name)


def coalesce(*pos):
    """
    Return the first positional argument that is not None. If all arguments are 
    None, or no arguments are provided, None is returned.
    """
    for value in pos:
        if value is not None:
            return value
    return None


def _test():
    """ Test this module. """
    import doctest
    import coalesce
    return doctest.testmod(coalesce)
