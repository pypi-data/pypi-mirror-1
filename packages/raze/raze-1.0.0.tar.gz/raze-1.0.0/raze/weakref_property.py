"""
RAZE Python Libraries
Weak-reference Property

The WeakRefProperty class is an attribute descriptor that stores values assigned 
to it as a weak reference.

    >>> class Bar(object):
    ...   pass

    >>> class Foo(object):
    ...   my_prop = WeakRefProperty()

    >>> f = Foo()
    >>> b = Bar()

    >>> f.my_prop is None
    True

    >>> f.my_prop = b
    >>> f.my_prop is b
    True

    >>> del b
    >>> f.my_prop is None
    True


$Id: weakref_property.py 256 2006-05-31 04:36:35Z james $
Copyright (c) 2006 James Harris
"""
__revision__ = "$Revision: 256 $"
__location__ = "$URL: http://localhost/svn/raze/tags/raze-1.0.0/raze/weakref_property.py $"
__all__ = [ 'WeakrefProperty' ]

from weakref import ref


class WeakRefProperty(object):
    """ Attribute descriptor that stores the assigned value as a weak-reference. """
    def __init__(self, attr_name=None, get=getattr, set=setattr, delete=delattr):
        super(WeakRefProperty, self).__init__()
        self.attr_name = attr_name or '_weakref_%x' % id(self)
        self._get = get
        self._set = set
        self._del = delete
    
    def make_reference(self, value):
        """ Return a weak-reference to the given value. """
        return ref(value)

    def __get__(self, instance, owner):
        try:
            value = self._get(instance, self.attr_name)
            if value is None:
                return None
            return value()
        except AttributeError:
            return None

    def __set__(self, instance, value):
        if value is not None:
            value = self.make_reference(value)
        self._set(instance, self.attr_name, value)

    def __delete__(self, instance):
        self._del(instance, self.attr_name)


def _test():
    """ Test this module. """
    import doctest
    import weakref_property
    return doctest.testmod(weakref_property)
