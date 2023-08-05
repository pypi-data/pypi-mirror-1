#!/usr/bin/python2.4
"""
RAZE Python Libraries

RAZE - Copyright (c) 2006 James Harris, Erin Houston
$Id: setup.py 258 2006-11-23 01:40:07Z james $
"""
__revision__ = "$Revision: 258 $"
__location__ = "$URL: http://icecave.svn.net.au/dav/lib/raze/tags/raze-1.1.0/setup.py $"

from distutils.core import setup
from os import linesep
import raze

def split_description():
    """ Fetch an array containing the strip()'ed rows of raze.__doc__. """
    docs = raze.__doc__
    if docs is None:
        return []
    docs = docs.strip()
    return [ line.strip() for line in docs.split(linesep) ]
split_description = split_description()

authors = [ 'James Harris', 'Erin Houston' ]

classifiers = [ 'Development Status :: 5 - Production/Stable',
                'Intended Audience :: Developers',
                'License :: Free To Use But Restricted',
                'Natural Language :: English',
                'Operating System :: OS Independent',
                'Programming Language :: Python',
                'Topic :: Software Development :: Libraries :: Python Modules' ]

packages = [ 'raze' ]

if __name__ == '__main__':
    setup(name='raze',
          version=raze.__version__,
          description=split_description[0] or None,
          long_description=linesep.join(split_description[1:-2]).strip() or None,
          author=', '.join(authors),
          author_email='raze@icecave.com.au',
          license=file('LICENSE').read(),
          url='http://www.icecave.com.au',
          download_url='http://www.icecave.com.au/assets/development/raze-%s.tar.gz' % raze.__version__,
          packages=packages,
          classifiers=classifiers)
