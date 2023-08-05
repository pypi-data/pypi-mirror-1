#!/usr/bin/python2.4
"""
RAZE Python Libraries
Run RAZE unit tests.

RAZE - Copyright (c) 2006 James Harris, Erin Houston
$Id: test.py 506 2006-12-14 05:03:08Z james $
"""
__revision__ = "$Revision: 506 $"
__location__ = "$URL: http://dev.icecave.com.au/main/dav/lib/raze/tags/raze-1.2.0/test.py $"

from sys import exit
from os.path import dirname
from raze.test import run_tests


if __name__ == '__main__':
    import raze
    import raze.coalesce
    import raze.container
    import raze.enumeration
    import raze.func
    import raze.import_
    import raze.logging_
    import raze.misc
    import raze.namestyle
    import raze.net
    import raze.optparse_
    import raze.password
    import raze.path
    import raze.phonetic
    import raze.property_
    import raze.singleton
    import raze.threading_
    import raze.transform
    import raze.visitor

    print 'Testing raze (using: %s).' % dirname(raze.__file__)
    failures, total = run_tests(raze.coalesce,
                                raze.container,
                                raze.enumeration,
                                raze.func,
                                raze.import_,
                                raze.logging_,
                                raze.misc,
                                raze.namestyle,
                                raze.net,
                                raze.optparse_,
                                raze.password,
                                raze.path,
                                raze.phonetic,
                                raze.property_,
                                raze.singleton,
                                raze.threading_,
                                raze.transform,
                                raze.visitor)
    print 'Testing complete, %d failures (%d tests performed).' % (failures, total)

    exit(failures)
