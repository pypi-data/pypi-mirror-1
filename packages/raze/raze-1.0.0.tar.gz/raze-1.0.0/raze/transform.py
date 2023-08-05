"""
RAZE Python Libraries
Multi-step Transformations.


Example of a two-step transformation, first convert the values to strings, then 
replace all 0's with 1's.

    >>> transform_chain = [ str, lambda s: s.replace('0', '1') ]
    >>> xform = CompoundTransform(transform_chain)
    >>> xform.apply(2010156, 1005, 10)
    ('2111156', '1115', '11')


If you apply a transform to a single value, a single transformed value is 
returned instead of a tuple.

    >>> xform.apply(2010156)
    '2111156'


To force the transform to return a tuple regardless of the input, specify the 
'force_tuple' keyword parameter.

    >>> xform.apply(2010156, force_tuple=True)
    ('2111156',)


There is also a helper function for easily transforming a single value.

    >>> transform(20105, *transform_chain)
    '21115'


Standard callable types can be used as transforms.

    >>> def test(value):
    ...   return value + 1
    >>> transform(42, test) 
    43


$Id: transform.py 256 2006-05-31 04:36:35Z james $
Copyright (c) 2006 James Harris
"""
__revision__ = "$Revision: 256 $"
__location__ = "$URL: http://localhost/svn/raze/tags/raze-1.0.0/raze/transform.py $"
__all__ = [ 'Transform', 'Identity', 'TransformAdapter', 'CompoundTransform', 'transform' ]

from protocols import AdaptationFailure, AbstractBase, advise, adapt


class Transform(AbstractBase):
    """ Base class for transformations. """
    def apply(self, *values, **kw):
        """ Apply the transformation. """
        pass

    def format_result(self, values, force_tuple=False):
        """
        Helper method for returning the result of apply to the user-requested 
        format.
        """
        if len(values) != 1 or force_tuple:
            return values
        return values[0]

    def __call__(self, *values):
        """ Alias for apply(). """
        return self.apply(*values)


class Identity(Transform):
    """ Identity transform. """
    def apply(self, *values, **kw):
        """ Apply the transformation. """
        return self.format_result(values, **kw)


class TransformAdapter(Transform):
    """ Adapts a unary callable to a tranform. """
    advise(instancesProvide  = [ Transform ],
           asAdapterForTypes = [ object ])

    def __init__(self, callable):
        super(Transform, self).__init__()
        self.callable = callable
    
    def apply(self, *values, **kw):
        """ Apply the transformation. """
        result = tuple(self.callable(v) for v in values)
        return self.format_result(result, **kw)


class CompoundTransform(Transform):
    """ Aggregate multiple transforms into a single transform object. """
    def __init__(self, transforms):
        super(Transform, self).__init__()
        self.transforms = [ adapt(xform, Transform, TransformAdapter(xform)) for xform in transforms ]
    
    def apply(self, *values, **kw):
        """ Apply the transformations. """
        for xform in self.transforms:
            values = xform.apply(force_tuple=True, *values)
        return self.format_result(values, **kw)


def transform(value, *transforms):
    """ Transform a single value using each of the given transforms sequentially. """
    return CompoundTransform(transforms).apply(value)


def _test():
    """ Test this module. """
    import doctest
    import transform
    return doctest.testmod(transform)
