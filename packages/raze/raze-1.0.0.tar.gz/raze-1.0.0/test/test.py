#!/usr/bin/python2.4
"""
RAZE Python Libraries
Run RAZE unit tests.

$Id: test.py 263 2006-05-31 05:50:02Z james $
Copyright (c) 2006 James Harris
"""
__revision__ = "$Revision: 263 $"
__location__ = "$URL: http://localhost/svn/raze/tags/raze-1.0.0/test/test.py $"

from sys import exit
from os.path import dirname
from raze.test import run_tests


if __name__ == '__main__':
    import raze
    import raze.container
    import raze.enumeration
    import raze.func
    import raze.lazy_import
    import raze.logging_
    import raze.misc
    import raze.namestyle
    import raze.phonetic
    import raze.proxy
    import raze.singleton
    import raze.threading_
    import raze.transform
    import raze.visitor
    import raze.weakref_property

    print 'Testing raze (using: %s).' % dirname(raze.__file__)
    failures, total = run_tests(raze.container,
                                raze.enumeration,
                                raze.func,
                                raze.lazy_import,
                                raze.logging_,
                                raze.misc,
                                raze.namestyle,
                                raze.phonetic,
                                raze.proxy,
                                raze.singleton,
                                raze.threading_,
                                raze.transform,
                                raze.visitor,
                                raze.weakref_property)
    print 'Testing complete, %d failures (%d tests performed).' % (failures, total)

    exit(failures)
