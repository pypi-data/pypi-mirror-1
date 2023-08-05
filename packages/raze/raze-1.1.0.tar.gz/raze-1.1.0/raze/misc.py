"""
RAZE Python Libraries
Miscellaneous functions and classes.


The SimpleObject class can be used to create simple objects which allow attribute 
creation (unlike the 'object' class).

    >>> x = SimpleObject()
    >>> x.foo = 123
    >>> x.foo
    123


Keyword parameters passed to SimpleObject's constructor become instance 
attributes.

    >>> x = SimpleObject(bar=111)
    >>> x.bar
    111


The join function provides a 'safe' implementation of the standard join. Before 
joining, each element in the sequence is converted to a string using the given 
format specifier.

    >>> sequence = [ 1, 2, 3 ]
    >>> join(sequence)
    '1, 2, 3'

    >>> join(sequence, separator='-')
    '1-2-3'

    >>> join(sequence, separator='-', format='(%s)')
    '(1)-(2)-(3)'


The conditional function takes an expression as it's first argument, if this 
expression evaluates to true the second argument is returned, otherwise the 
third argument is returned.

    >>> conditional(True, 1, 2)
    1

    >>> conditional(False, 1, 2)
    2


Return a dictionary of an object's attributes.

    >>> obj = object()
    >>> attribute_dict(obj) 
    {}

    >>> attribute_dict(obj, None) is None
    True


    >>> class UsesSlots(object):
    ...   __slots__ = ('a', 'b', 'c')
    ...   def __init__(self):
    ...     self.a = 100

    >>> obj = UsesSlots()
    >>> attribute_dict(obj)
    {'a': 100}

RAZE - Copyright (c) 2006 James Harris, Erin Houston
$Id: misc.py 258 2006-11-23 01:40:07Z james $
"""
__revision__ = "$Revision: 258 $"
__location__ = "$URL: http://icecave.svn.net.au/dav/lib/raze/tags/raze-1.1.0/raze/misc.py $"
__all__ = [ 'SimpleObject', 'join', 'conditional', 'attribute_dict' ]

from container import conform_list


class SimpleObject(object):
    """ Empty object (overrides __slots__ effect of object class). """
    def __init__(self, **kw):
        super(SimpleObject, self).__init__()
        self.__dict__.update(kw)


def join(sequence, separator=', ', format='%s'):
    """
    Safe implementation of string.join(). All elements of sequence are converted 
    to strings first using the provide format spec. Separator defaults to ', '.
    """
    strings = [format % element for element in sequence]
    return separator.join(strings)


def conditional(condition, true_value, false_value):
    """
    Loose emulation of the ternary operator (?:). Returns true_value if 
    condition is True, otherwise returns false_value.
    """
    if condition:
        return true_value
    return false_value


def attribute_dict(obj, default={}):
    """
    Return a dictionary of an object's attributes, even if the object uses slots.
    If there is no way to determine how to obtain the object's attributes, the 
    value of default is returned (defaults to an empty dictionary).
    """
    if hasattr(obj, '__dict__'):
        return dict(obj.__dict__)
    if hasattr(obj, '__slots__'):
        slots = conform_list(obj.__slots__)
        pairs = [ (name, getattr(obj, name)) for name in slots if hasattr(obj, name) ]
        return dict(pairs)
    return default


def _test():
    """ Test this module. """
    import doctest
    import misc
    return doctest.testmod(misc)
