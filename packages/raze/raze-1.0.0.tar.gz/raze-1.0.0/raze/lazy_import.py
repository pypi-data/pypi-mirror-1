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


$Id: lazy_import.py 256 2006-05-31 04:36:35Z james $
Copyright (c) 2006 James Harris
"""
__revision__ = "$Revision: 256 $"
__location__ = "$URL: http://localhost/svn/raze/tags/raze-1.0.0/raze/lazy_import.py $"
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
    import lazy_import
    return doctest.testmod(lazy_import)
