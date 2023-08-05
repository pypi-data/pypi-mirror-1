"""Magic function.

This module defines a function that will convert any other pre-existing
function into one able to manipulate Pydods objects.

Suppose you have a function called 'detrend', which detrends data along an
axis, and you want to use it with a GridType object called 'sst'. You
would simply do something like this:

    >>> detrend = fluid.dtypize(detrend)
    >>> detrended_data = detrend(sst)

Notice that here the function returns the detrended *data*, not a GridType
object. If you want the function to return a modified object that was 
passed as a parameter, specify the parameter position when dtypifying it:

    >>> detrend = fluid.dtypize(detrend, 0)
    >>> sst = detrend(sst)

Here, the function now returns the 'sst' object modified, with its data
detrended. The index specification is necessary because some functions
can accept multiple objects as parameters:

    def foo(int, grid, constant):
        ...

So in this case, you must say that you want it to return the grid object:

    foo = dtypize(foo, 1)

Is it clear? ;-)
"""

__version__ = "$Revision: 15 $"
# $Source$

from fluid import dtypes


class dtypize:
    def __init__(self, func, retobj=None):
        self.func = func
        self.retobj = retobj

    def __call__(self, *args, **kwargs):
        newargs = []
        for arg in args:
            if isinstance(arg, dtypes.BaseType):
                newargs.append(arg.data)
            else:
                newargs.append(arg)
        newargs = tuple(newargs)

        newkwargs = {}
        for k,v in kwargs:
            if isinstance(v, dtypes.BaseType):
                newkwargs[k] = v.data
            else:
                newkwargs[k] = v

        if self.retobj is not None:
            args[self.retobj].data = self.func(*newargs, **newkwargs)
            return args[self.retobj]

        return self.func(*newargs, **newkwargs)


if __name__ == '__main__':
    import numarray

    def sum_one(data):
        return data + 1
    sum_one      = dtypize(sum_one)     # returns array
    sum_one_zero = dtypize(sum_one, 0)  # returns modified 'data' (position 0) object

    a = numarray.array([1,2,3])
    print 'Passing simple array to sum_one...'
    print sum_one(a)

    # Create a GridType object.
    b = dtypes.GridType()
    b.array = dtypes.ArrayType()
    b.array.data = numarray.array([1,2,3])
    b.array.dimensions = ('x',)
    b.maps['x'] = dtypes.ArrayType()
    b.maps['x'].data = numarray.arange(3)
    
    print 'Passing GridType to sum_one...'
    c = sum_one(b)
    print 'Should return an array...'
    print c

    print 'Passing GridType to sum_one_zero...'
    d = sum_one_zero(b)
    print 'Should return same object as was passed...'
    print 'This is the object:'
    print d
    print 'And this is the data:'
    print d.array[:]
