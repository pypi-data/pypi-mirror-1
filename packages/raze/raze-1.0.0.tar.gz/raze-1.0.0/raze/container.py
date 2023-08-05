"""
RAZE Python Libraries
Extended container types and utilities.


Merge two or more dictionaries with the merge_dictionaries functions.
Values from dictionaries later (further right) in the argument list replace 
those with the same keys from earlier dictionaries.

    >>> dict_1 = { 'a' : 1, 'b' : 2 }
    >>> dict_2 = { 'b' : 3, 'c' : 4 }
    >>> dict_3 = { 'c' : 5, 'd' : 6 }
    >>> merged = merge_dictionaries(dict_1, dict_2, dict_3)
    >>> len(merged)
    4

    >>> merged['a'], merged['b'], merged['c'], merged['d']
    (1, 3, 5, 6)


Swap a dictionary's keys and values with the invert_dictionary function.

    >>> my_dict = { 'a' : 1, 'b' : 2, 'c' : 3, 'd' : 3 }
    >>> inverse = invert_dictionary(my_dict)
    >>> len(inverse)
    3

    >>> inverse[1], inverse[2], inverse[3]
    ('a', 'b', 'd')


The xzip function is like zip(), but instead of returning a list, returns an 
object that generates the zipped sequence on demand.

    >>> seq_1 = [ 1, 2, 3, 4, 5 ]
    >>> seq_2 = [ 'a', 'b', 'c', 'd' ]
    >>> seq_3 = [ 'x', 'y', 'z' ]
    
    >>> for p, q, r in xzip(seq_1, seq_2, seq_3):
    ...     print p, q, r
    1 a x
    2 b y
    3 c z


The xenumerate function is like enumerate(), but instead of returning a list, 
returns an object that generates the enumerated sequence in demand.

    >>> sequence = [ 'a', 'b', 'c' ]
    >>> for index, element in xenumerate(sequence):
    ...     print index, element
    0 a
    1 b
    2 c

    >>> sequence = [ 'a', 'b', 'c', 'd', 'e' ]
    >>> list(even_elements(sequence))
    ['a', 'c', 'e']

    >>> list(odd_elements(sequence))
    ['b', 'd']


A BidirectionalDictionary maintains key -> value relationships in both 
directions.

    >>> input_1 = { 1 : 2 }
    >>> bd = BidirectionalDictionary(input_1)
    >>> bd[1], bd[2]
    (2, 1)
    
    >>> bd.setdefault('foo', 'bar')
    >>> bd['foo'], bd['bar']
    ('bar', 'foo')

    >>> input_2 = { 'a' : 'b' }
    >>> bd.update(input_2)
    >>> bd['a'], bd['b']
    ('b', 'a')

    >>> copy = bd.copy()
    >>> isinstance(copy, BidirectionalDictionary)
    True

    >>> copy == bd
    True

    >>> copy is bd
    False


$Id: container.py 256 2006-05-31 04:36:35Z james $
Copyright (c) 2006 James Harris
"""
__revision__ = "$Revision: 256 $"
__location__ = "$URL: http://localhost/svn/raze/tags/raze-1.0.0/raze/container.py $"
__all__ = [ 'merge_dictionaries', 'invert_dictionary', 'xzip', 'xenumerate', 'even_elements', 'odd_elements', 'BidirectionalDictionary' ]


def merge_dictionaries(dictionary, *dictionaries):
    """ Create a new dictionary with all elements from the given dictionaries. """
    dictionary = dictionary.copy()
    for dict in dictionaries:
        dictionary.update(dict)
    return dictionary


def invert_dictionary(dictionary):
    """ Return the 'inverse' of the given dictionary (values become keys). """
    return dict(reversed(item) for item in dictionary.iteritems())


def xzip(*sequences):
    """
    Like zip(), but instead of returning a list, returns an object that 
    generates the zipped sequence on demand.
    """
    if sequences:
        iters = [ iter(s) for s in sequences ]
        while True:
            yield tuple([ i.next() for i in iters ])


def xenumerate(sequence):
    """
    Like enumerate(), but instead of returning a list, returns an object that 
    generates the enumerated sequence in demand.
    """
    counter = 0
    for element in sequence:
        yield counter, element
        counter += 1


def even_elements(sequence):
    """ Yield only the even elements of a sequence. """
    i = iter(sequence)
    while True:
        yield i.next()
        i.next()


def odd_elements(sequence):
    """ Yield only the even elements of a sequence. """
    i = iter(sequence)
    while True:
        i.next()
        yield i.next()


class BidirectionalDictionary(dict):
    """ Dictionary that maintains key -> value relationships in both directions. """
    def __init__(self, *pos, **kw):
        super(BidirectionalDictionary, self).__init__(*pos, **kw)
        self.resolve()

    def __setitem__(self, key, value):
        super(BidirectionalDictionary, self).__setitem__(key, value)
        super(BidirectionalDictionary, self).__setitem__(value, key)

    def setdefault(self, key, value):
        super(BidirectionalDictionary, self).setdefault(key, value)
        super(BidirectionalDictionary, self).setdefault(value, key)

    def update(self, *pos, **kw):
        super(BidirectionalDictionary, self).update(*pos, **kw)
        self.resolve()
    
    def resolve(self):
        """ Ensure that bidirectional mappings are maintained. """
        value_set = set()
        for key, value in self.items():
            if value in value_set:
                del self[key]
            else:
                value_set.add(key)
        inverse = invert_dictionary(self)
        super(BidirectionalDictionary, self).update(inverse)

    def copy(self):
        return type(self)(self)

    def fromkeys(self, sequence):
        for value in zip(sequence, sequence):
            super(BidirectionalDictionary).__setitem__(value, value)
        raise AttributeError('%s does not support fromkeys()' % type(self).__name__)


def _test():
    """ Test this module. """
    import doctest
    import container
    return doctest.testmod(container)
