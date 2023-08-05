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


The coalesce function returns the first of its arguments that is not None.
None is returned only if all arguments are None or no arguments are provided.

    >>> coalesce(None, None, 46, 2) == 46
    True

    >>> coalesce(None, None) is None
    True

    >>> coalesce() is None
    True


The conditional function takes an expression as it's first argument, if this 
expression evaluates to true the second argument is returned, otherwise the 
third argument is returned.

    >>> conditional(True, 1, 2)
    1

    >>> conditional(False, 1, 2)
    2


$Id: misc.py 256 2006-05-31 04:36:35Z james $
Copyright (c) 2006 James Harris
"""
__revision__ = "$Revision: 256 $"
__location__ = "$URL: http://localhost/svn/raze/tags/raze-1.0.0/raze/misc.py $"
__all__ = [ 'SimpleObject', 'join', 'sink', 'coalesce', 'conditional' ]


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


def sink(*pos, **kw):
    """ Takes any arguments, does nothing, returns nothing. """
    pass


def coalesce(*pos):
    """
    Return the first positional argument that is not None. If all arguments are 
    None, or no arguments are provided, None is returned.
    """
    for value in pos:
        if value is not None:
            return value
    return None


def conditional(condition, true_value, false_value):
    """
    Loose emulation of the ternary operator (?:). Returns true_value if 
    condition is True, otherwise returns false_value.
    """
    if condition:
        return true_value
    return false_value


def _test():
    """ Test this module. """
    import doctest
    import misc
    return doctest.testmod(misc)
