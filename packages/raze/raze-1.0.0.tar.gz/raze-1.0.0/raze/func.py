"""
RAZE Python Libraries
Function utils and functional programming tools.


The Arguments class stores positional and keywords arguments, and may be used to 
apply them to a callable object.

    >>> def my_func(foo, bar, spam):
    ...   print 'foo:  %s' % foo
    ...   print 'bar:  %s' % bar
    ...   print 'spam: %s' % spam

    >>> args = Arguments(1, 2, spam=3)
    >>> args.apply(my_func)
    foo:  1
    bar:  2
    spam: 3


You can combine two sets of arguments using the combine() method (the + operator 
is an alias for combine). Positional arguments are appended, keyword arguments 
are replaced using dict's update() method.

    >>> args1 = Arguments(1, 2, foo='foo', bar='bar')
    >>> args2 = Arguments(3, 4, spam='spam', foo='doom')
    >>> args3 = args1 + args2

    >>> args3.positional
    [1, 2, 3, 4]

    >>> keys = args3.keyword.keys()
    >>> keys.sort()
    >>> keys
    ['bar', 'foo', 'spam']

    >>> [ args3.keyword[k] for k in keys ]
    ['bar', 'doom', 'spam']


$Id: func.py 256 2006-05-31 04:36:35Z james $
Copyright (c) 2006 James Harris
"""
__revision__ = "$Revision: 256 $"
__location__ = "$URL: http://localhost/svn/raze/tags/raze-1.0.0/raze/func.py $"
__all__ = [ 'Arguments' ]

from misc import join


class Arguments(object):
    """ Store positional and keyword arguments. """
    def __init__(self, *pos, **kw):
        super(Arguments, self).__init__()
        self.positional = list(pos)
        self.keyword = kw

    def apply(self, func):
        """ Call the given function with the stored arguments. """
        return func(*self.positional, **self.keyword)

    def update(self, *pos, **kw):
        """
        Update the stored positional and keyword arguments.
        Positional arguments are appended, keyword arguments are added/replaced.
        """
        self.positional += list(pos)
        self.keyword.update(kw)

    def combine(self, other):
        """
        Create a new Arguments object and update() it with values from self, 
        then other.
        """
        args = type(self)()
        args.update(*self.positional, **self.keyword)
        args.update(*other.positional, **other.keyword)
        return args

    def __add__(self, other):
        """ Alias for combine() """
        return self.combine(other)

    def __str__(self):
        pos = join(self.positional, format='%r')
        kw  = join(self.keyword.iteritems(), format='%s=%r')
        return join(item for item in (pos, kw) if item)

    def __repr__(self):
        return '%s(%s)' % (type(self).__name__, self)


def _test():
    """ Test this module. """
    import doctest
    import func
    return doctest.testmod(func)
