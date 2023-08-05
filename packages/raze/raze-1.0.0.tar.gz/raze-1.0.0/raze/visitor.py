"""
RAZE Python Libraries
Semi-automated visitor pattern.


The 'visitor_method' property of a visitee determines which method to call. By 
default it uses raze.NameStyleConverter to conver the visitee's class name to 
'lower' style, and prefixes it with 'visit_'.

    >>> class VisiteeWithLongName(Visitee): pass
    >>> visitee = VisiteeWithLongName()
    >>> visitee.visitor_method(VisiteeWithLongName)
    'visit_visitee_with_long_name'


The visitor object is written with methods matching the .visitor_method for each 
type it needs to handle. Following is a visitor that handles visitation of Foo 
and Bar objects.

    >>> class MyVisitor(Visitor):
    ...   def visit_foo(self, obj):
    ...     print 'Visited a Foo!'
    ...   def visit_bar(self, obj):
    ...     print 'Visited a Bar!'
    >>> visitor = MyVisitor()

    >>> class Foo(Visitee): pass
    >>> class Bar(Visitee): pass
    >>> class Baz(Visitee): pass
    >>> foo = Foo()
    >>> bar = Bar()
    >>> baz = Baz()

    >>> foo.accept_visitor(visitor)
    Visited a Foo!

    >>> bar.accept_visitor(visitor)
    Visited a Bar!


Attempting to visit an unsupported visitor type raises a VisitError.   

    >>> baz.accept_visitor(visitor)
    Traceback (most recent call last):
    VisitError: MyVisitor does not support visitation of Baz.


You can also use the free helper function which adapts the arguments to the 
appropriate type first.

    >>> visit(foo, visitor)
    Visited a Foo!


By default a visitee traverses it's MRO (method resolution order) looking for a method to call.
This provides support for inheritance.

    >>> class Spam(Foo): pass
    >>> spam = Spam()
    >>> spam.accept_visitor(visitor)
    Visited a Foo!


$Id: visitor.py 256 2006-05-31 04:36:35Z james $
Copyright (c) 2006 James Harris
"""
__revision__ = "$Revision: 256 $"
__location__ = "$URL: http://localhost/svn/raze/tags/raze-1.0.0/raze/visitor.py $"
__all__ = [ 'VisitError', 'Visitor', 'Visitee', 'visit' ]

from inspect import getmro
from protocols import adapt
from namestyle import NameStyleConverter


class VisitError(TypeError):
    """ A visitor does not support the type of the visitee. """
    pass


class Visitor(object):
    """ Base class for visitors. """
    def visit_visitee(self, visitee):
        """ Default visitee handler - raises a VisitError """
        raise VisitError('%s does not support visitation of %s.' % (type(self).__name__, type(visitee).__name__))


class Visitee(object):
    """ Base class for objects that may be visited. """
    visitor_method_format = 'visit_%s'

    def visitor_method(self, class_):
        """
        Return the name of the method to attempt to call when visting objects of 
        this type.
        """
        converter = NameStyleConverter(class_.__name__)
        return self.visitor_method_format % converter.lower

    def visitor_mro(self):
        """
        Return a list of methods to attempt to call on the visitor passed to 
        self.accept_visitor().
        """
        return [ self.visitor_method(class_) for class_ in getmro(type(self)) ]
        
    def accept_visitor(self, visitor):
        """
        Look for a method of visitor with the name returned by 
        self.visitor_method and call it with self as the only parameter. If 
        visitor does not have such an attribute call visitor.visit(self) 
        instead.
        """
        visitor = adapt(visitor, Visitor)
        for name in self.visitor_mro():
            if hasattr(visitor, name):
                return getattr(visitor, name)(self)
        # this should never be reached as Visitor supplies a function that 
        # anything derived from Visitee well fall back to.
        assert(False)


def visit(visitee, visitor):
    """
    Helper function that adapts the given visitee to the Visitee interface 
    before calling visitee.accept_visitor(visitor).
    """
    visitee = adapt(visitee, Visitee)
    return visitee.accept_visitor(visitor)


def _test():
    """ Test this module. """
    import doctest
    import visitor
    return doctest.testmod(visitor)
