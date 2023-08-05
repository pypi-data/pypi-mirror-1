"""
RAZE Python Libraries
Internal test utility.


RAZE - Copyright (c) 2006 James Harris, Erin Houston
$Id: test.py 258 2006-11-23 01:40:07Z james $
"""
__revision__ = "$Revision: 258 $"
__location__ = "$URL: http://icecave.svn.net.au/dav/lib/raze/tags/raze-1.1.0/raze/test.py $"
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
