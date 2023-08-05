"""
RAZE Python Libraries
Lazy module access.


This class is useful when a module cannot be imported into the global namespace 
due to cyclic dependencies.

    >>> class TestLazyImport(LazyImport):
    ...   def import_(self):
    ...      import misc
    ...      return misc

    >>> mod = TestLazyImport()
    >>> mod.SimpleObject
    <class 'raze.misc.SimpleObject'>


RAZE - Copyright (c) 2006 James Harris, Erin Houston
$Id: import_.py 258 2006-11-23 01:40:07Z james $
"""
__revision__ = "$Revision: 258 $"
__location__ = "$URL: http://icecave.svn.net.au/dav/lib/raze/tags/raze-1.1.0/raze/import_.py $"
__all__ = [ 'LazyImport' ]


class LazyImport(object):
    """
    Lazy module importer.
    Acts as a proxy for a given module, importing it upon first use.
    """
    __slots__ = ('__module')

    def __init__(self):
        super(LazyImport, self).__init__(self)
        self.__module = None

    def __getattr__(self, name):
        return getattr(self.module, name)
    
    def __setattr__(self, name, value):
        if name == '_LazyImport__module':
            return super(LazyImport, self).__setattr__(name, value)
        return setattr(self.module, name, value)

    def __delattr__(self, name):
        return delattr(self.module, name)

    @property
    def module(self):
        """ Return the module, possibly importing it. """
        if self.__module is None:
            self.__module = self.import_()
        return self.__module

    def import_(self):
        """ Import and return the module. """
        pass


def _test():
    """ Test this module. """
    import doctest
    import import_
    return doctest.testmod(import_)
