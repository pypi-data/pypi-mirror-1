#!/usr/bin/python2.4
"""
RAZE Python Libraries
Run RAZE unit tests.

RAZE - Copyright (c) 2006 James Harris, Erin Houston
$Id: test.py 258 2006-11-23 01:40:07Z james $
"""
__revision__ = "$Revision: 258 $"
__location__ = "$URL: http://icecave.svn.net.au/dav/lib/raze/tags/raze-1.1.0/test.py $"

from sys import exit
from os.path import dirname
from raze.test import run_tests


if __name__ == '__main__':
    import raze
    import raze.container
    import raze.coalesce
    import raze.enumeration
    import raze.func
    import raze.import_
    import raze.logging_
    import raze.misc
    import raze.namestyle
    import raze.net
    import raze.phonetic
    import raze.singleton
    import raze.threading_
    import raze.transform
    import raze.visitor
    import raze.weakprop

    print 'Testing raze (using: %s).' % dirname(raze.__file__)
    failures, total = run_tests(raze.container,
                                raze.coalesce,
                                raze.enumeration,
                                raze.func,
                                raze.import_,
                                raze.logging_,
                                raze.misc,
                                raze.namestyle,
                                raze.net,
                                raze.phonetic,
                                raze.singleton,
                                raze.threading_,
                                raze.transform,
                                raze.visitor,
                                raze.weakprop)
    print 'Testing complete, %d failures (%d tests performed).' % (failures, total)

    exit(failures)
