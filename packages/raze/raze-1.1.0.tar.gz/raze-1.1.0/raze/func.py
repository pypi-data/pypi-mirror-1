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


The MROCall class provides a mechanism for searching an object's inheritance 
hierarchy for methods matching a given name. It then calls each of these methods 
in turn according to the MRO (method resolution order).

    >>> class Foo(object):
    ...   def my_method(self, arg):
    ...     return 'Foo: %r' % arg

    >>> class Bar(Foo):
    ...   def my_method(self, arg):
    ...     return 'Bar: %r' % arg

    >>> class Spam(Bar):
    ...   def my_method(self, arg):
    ...     return 'Spam: %r' % arg

    >>> obj = Spam()
    >>> call = MROCall(obj)

The simplest way to call a method is to access the method by name as an 
attribute of the MROCall object:

    >>> results = call.my_method('Hello, world!')

This will give a generator that calls each method and yields the result. (Note 
that the methods are not actually called until the generator is iterated over)

    >>> for result in results:
    ...   print result
    Foo: 'Hello, world!'
    Bar: 'Hello, world!'
    Spam: 'Hello, world!'

By default the methods are executed in REVERSE order to the MRO, so that methods 
higher in the inheritance hierarchy are called earlier. This behavior can be 
changed by specifying reverse=False when constructing the MROCall object.


If no matching methods are found an AttributeError is raised.

    >>> call.fake_method
    Traceback (most recent call last):
    AttributeError: fake_method


The defer() function invokes a callable object in parallel to the current 
thread, giving the result when available.

    >>> def my_callable(arg):
    ...   return 'I was called: %s' % arg;
    
    >>> f = defer(my_callable, 'Hello, world.')
    >>> print f.result
    I was called: Hello, world.


RAZE - Copyright (c) 2006 James Harris, Erin Houston
$Id: func.py 258 2006-11-23 01:40:07Z james $
"""
__revision__ = "$Revision: 258 $"
__location__ = "$URL: http://icecave.svn.net.au/dav/lib/raze/tags/raze-1.1.0/raze/func.py $"
__all__ = [ 'Arguments', 'MROCall', 'DeferredCall', 'defer', 'sink', 'identity' ]

from inspect import getmro
from misc import join
from threading_ import Thread


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


class MROCall(object):
    """ Proxy to call a named method from each class in an objects MRO. """
    def __init__(self, object, reverse=True):
        super(MROCall, self).__init__()
        self.object = object
        self.reverse = reverse

    def filter(self, class_, method_name):
        """
        Determines which methods will be called. Default filter allows any 
        attribute matching the given name that is callable. Raises an attribute 
        error if the named method is not to be used, otherwise return the 
        method. May be overridden.
        """
        method = getattr(class_, method_name)
        if callable(method):
            return method
        raise AttributeError(method_name)

    def methods(self, method_name):
        """ Yield matching methods. """
        def methods():
            object_class = type(self.object)
            for class_ in getmro(object_class):
                try:
                    yield self.filter(class_, method_name)
                except AttributeError:
                    pass
        methods = list(methods())
        if self.reverse:
            methods.reverse()
        return methods

    def generator(self, method_name, *pos, **kw):
        """ Call matching methods, YIELDING 2-tuples of (method, result). """
        for method in self.methods(method_name):
            yield method, method(self.object, *pos, **kw)
    
    def as_tuples(self, method_name, *pos, **kw):
        """
        Call matching methods, returning the results as a list of 2-tuples of 
        (method, result).
        """
        return list(self.generator(method_name, *pos, **kw))
    
    def as_dict(self, method_name, *pos, **kw):
        """
        Call matching methods, returning the results as a dictionary mapping 
        method to result.
        """
        return dict(self.generator(method_name, *pos, **kw))

    def as_list(self, method_name, *pos, **kw):
        """ Call matching methods, returning a list of the results. """
        return [ result for method, result in self.generator(method_name, *pos, **kw) ]
        
    def __call__(self, method_name, *pos, **kw):
        """ Call matching methods, yielding the results. """
        for method in methods:
            yield method(self.object, *pos, **kw)

    def __make_proxy(self, method_name, exception):
        methods = self.methods(method_name)
        if not methods:
            raise exception(method_name)
        def proxy(*pos, **kw):
            for method in methods:
                yield method(self.object, *pos, **kw)
        proxy.__name__ = method_name
        return proxy

    def __getitem__(self, method_name):
        return self.__make_proxy(method_name, KeyError)
    
    def __getattr__(self, method_name):
        return self.__make_proxy(method_name, AttributeError)


class DeferredCall(Thread):
    def __init__(self, callable, *pos, **kw):
        super(DeferredCall, self).__init__()
        self.callable = callable
        self.arguments = Arguments(*pos, **kw)
        self.started = False

    def start(self):
        self.started = True
        self.setName('deferred call to %r' % self.callable)
        return super(DeferredCall, self).start()
    
    def run(self):
        self._result = self.arguments.apply(self.callable)
    
    @property
    def result(self):
        """ Join the executor thread and return the result. """
        self.join()
        return self._result


def defer(callable, *pos, **kw):
    """ Invoke a callable in parallel to the current thread of execution. """
    dc = DeferredCall(callable, *pos, **kw)
    dc.start()
    return dc


def sink(*pos, **kw):
    """ Takes any arguments, does nothing, returns nothing. """
    pass


def identity(value):
    """ Takes a single argument and returns it. """
    return value


def _test():
    """ Test this module. """
    import doctest
    import func
    return doctest.testmod(func)
