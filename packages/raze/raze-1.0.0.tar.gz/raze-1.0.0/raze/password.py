"""
RAZE Python Libraries
Password generation and other utilities.


$Id: password.py 256 2006-05-31 04:36:35Z james $
Copyright (c) 2006 James Harris
"""
__revision__ = "$Revision: 256 $"
__location__ = "$URL: http://localhost/svn/raze/tags/raze-1.0.0/raze/password.py $"
__all__ = [ 'generate_password' ]

from random import choice, randint
from phonetic import character_set


def generate_password(min_length=8, max_length=None, **kw):
    """
    Generate a password.
    kw is a dictionary where the keys are the name of any of the character sets 
    in phonetic.character_set the value indicates whether to allow characters of 
    that class in the password.  The default classes to use are 'lower_case', 
    'upper_case', and 'digits'.
    """
    if not kw:
        kw['lower_case'] = True
        kw['upper_case'] = True
        kw['digits'] = True

    charset = []
    for charset_name, allow in kw.iteritems():
        if allow:
            charset += getattr(character_set, charset_name).keys()

    if max_length == None:
        max_length = min_length
    
    length = randint(min_length, max_length)
    result = [ choice(charset) for index in xrange(length) ]
    return str().join(result)
