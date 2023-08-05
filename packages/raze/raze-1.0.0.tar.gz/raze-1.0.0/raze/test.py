"""
RAZE Python Libraries
Internal test utility.


$Id: test.py 256 2006-05-31 04:36:35Z james $
Copyright (c) 2006 James Harris
"""
__revision__ = "$Revision: 256 $"
__location__ = "$URL: http://localhost/svn/raze/tags/raze-1.0.0/raze/test.py $"
__all__ = [ 'run_tests' ]


def run_tests(*modules):
    """ Call the _test() function on each of the given modules. """
    errors = 0
    total  = 0
    for module in modules:
        if not hasattr(module, '_test') or not callable(module._test):
            print 'Warning: %s does not define a _test() function.' % module
            errors += 1
            continue
        
        try:
            fails, count = module._test()
            errors += fails
            total  += count
            if not total:
                print 'Warning: %s has no tests.' % module
                errors += 1                
        
        except Exception, e:
            print 'Exception: %s: %s' % (e.__class__.__name__, e)
            errors += 1

    return errors, total
