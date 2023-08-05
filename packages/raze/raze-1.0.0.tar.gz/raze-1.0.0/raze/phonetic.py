"""
RAZE Python Libraries
NATO Phonetic Dictionary.


    >>> pd = PhoneticDictionary()
    >>> pd.spell('Phonetic Dictionary!')
    'PAPA-hotel-oscar-november-echo-tango-india-charlie DELTA-india-charlie-tango-india-oscar-november-alfa-romeo-yankee-EXCLAMATION'

    >>> pd.spell('Here are some digits: 1 2 3 4 5')
    'HOTEL-echo-romeo-echo alfa-romeo-echo sierra-oscar-mike-echo delta-india-golf-india-tango-sierra-COLON WUN TOO TREE FOWER FIFE'


$Id: phonetic.py 256 2006-05-31 04:36:35Z james $
Copyright (c) 2006 James Harris
"""
__revision__ = "$Revision: 256 $"
__location__ = "$URL: http://localhost/svn/raze/tags/raze-1.0.0/raze/phonetic.py $"
__all__ = [ 'PhoneticDictionary', 'character_set' ]

from re import compile
from container import BidirectionalDictionary


class character_set(object):
    """ Character set dictionaries. """
    lower_case  = { 'a' : 'alfa', 'b' : 'bravo', 'c' : 'charlie', 'd' : 'delta', 'e' : 'echo', 'f' : 'foxtrot', 'g' : 'golf', 'h' : 'hotel', 'i' : 'india', 'j' : 'juliett', 'k' : 'kilo', 'l' : 'lima', 'm' : 'mike', 'n' : 'november', 'o' : 'oscar', 'p' : 'papa', 'q' : 'quebec', 'r' : 'romeo', 's' : 'sierra', 't' : 'tango', 'u' : 'uniform', 'v' : 'victor', 'w' : 'whiskey', 'x' : 'xray', 'y' : 'yankee', 'z' : 'zulu' }
    upper_case  = dict((k.upper(), v.upper()) for k, v in lower_case.iteritems())
    punctuation = { '!' : 'EXCLAMATION', '\'' : 'SINGLE_QUOTE', '"' : 'DOUBLE_QUOTE', '#' : 'HASH', '$' : 'DOLLAR', '%' : 'PERCENT', '&' : 'AMPERSAND', '(' : 'LEFT_PARENTHESIS', ')' : 'RIGHT_PARENTHESIS', '*' : 'ASTERISK', '+' : 'PLUS', ',' : 'COMMA', '-' : 'MINUS', '.' : 'PERIOD', '/' : 'SLASH', ':' : 'COLON', ';' : 'SEMICOLON', '<' : 'LESS', '=' : 'EQUAL', '>' : 'GREATER', '?' : 'QUESTION', '@' : 'AT', '[' : 'LEFT_BRACKET', ']' : 'RIGHT_BRACKET', '\\' : 'BACKSLASH', '^' : 'HAT', '_' : 'UNDERSCORE', '`' : 'BACKTICK', '{' : 'LEFT_BRACE', '|' : 'PIPE', '}' : 'RIGHT_BRACE', '~' : 'TILDE' }
    digits      = { '0' : 'ZERO', '1' : 'WUN', '2' : 'TOO', '3' : 'TREE', '4' : 'FOWER', '5' : 'FIFE', '6' : 'SIX', '7' : 'SEVEN', '8' : 'AIT', '9' : 'NINER' }

    all = {}
    all.update(lower_case)
    all.update(upper_case)
    all.update(punctuation)
    all.update(digits)


class PhoneticDictionary(dict):
    """ NATO Phonetic alphabet dictionary. """
    whitespace_pattern = compile('(\s+)')

    def __init__(self, character_set=character_set.all):
        super(PhoneticDictionary, self).__init__(character_set)

    def translate(self, char):
        return self.get(char, char)

    def spell(self, text, seperator='-'):
        """
        Spell the given text, seperating terms by the given seperator. Any 
        character in text that is not in the NATO alphabet is left as-is.
        """
        sequence = self.whitespace_pattern.split(text)
        for index, word in enumerate(sequence):
            if index % 2 == 0:
                sequence[index] = seperator.join(self.translate(char) for char in word)
        return str().join(sequence)


def _test():
    """ Test this module. """
    import doctest
    import phonetic
    return doctest.testmod(phonetic)
