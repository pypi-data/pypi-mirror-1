#!/usr/bin/python2.4
"""
RAZE Python Libraries

$Id: setup.py 265 2006-05-31 10:26:07Z james $
Copyright (c) 2006 James Harris
"""
__revision__ = "$Revision: 265 $"
__location__ = "$URL: http://localhost/svn/raze/tags/raze-1.0.0/setup.py $"

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

authors = [ 'James Harris' ]

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
          url='http://wiki.icecave.com.au/index.php/Raze',
          download_url='http://www.icecave.com.au/assets/development/raze-%s.tar.gz' % raze.__version__,
          packages=packages,
          classifiers=classifiers)
