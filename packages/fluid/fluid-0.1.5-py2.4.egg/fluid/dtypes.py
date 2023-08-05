"""Objects from OPeNDAP.

Thses objects represent the types defined in the DAP 2 specification. They
are returned when accessing a DAP dataset using the Pydods module, but can
(should!) also be used in other contexts, since they store metainformation
about grids, types, dimensions, units and much more.

The most useful object is the GridType. A GridType is nothing more than an
array with stored information about its dimensions. An example for a SST
map called 'sst':

    >>> isinstance(sst, dtypes.GridType)
    True
    >>> print sst.dimensions
    ('latitude', 'longitude')
    >>> print sst.shape
    (90, 180)
    >>> print sst.units
    C
    >>> print sst.array
    <fluid.dtypes.ArrayType object at 0x401fd92c>
    >>> print sst.array[0,0]  # get some data
    [23.4, 23.3]

You can do much more. If you slice a GridType, the result is a new
GridType with the data sliced, and also the dimensions sliced:

    >>> sst2 = sst[:10,:10]
    >>> isinstance(sst, dtypes.GridType)
    True
    >>> print sst2.dimensions
    ('latitude', 'longitude')
    >>> print sst.shape
    (10, 10)
    
Have fun!    
"""

__version__ = "$Revision: 7 $"
# $Source$

import copy

import numarray


# Conversion from numarray and Pydods types.
typeconvert = {'1': 'Byte', 's': 'Int16', 'i': 'Int32', 'l': 'Int32',
               'b': 'Uint16', 'w': 'Uint16', 'u': 'Uint32',
               'f': 'Float32', 'd': 'Float64',
               'c': 'String'}


class BaseType(object):
    def __init__(self):
        self.data = None
        self.attributes = {}

    def __getitem__(self, index):
        # Return data.
        return self.data


class ArrayType(BaseType):
    def __init__(self):
        self.data = numarray.array([])
        self.attributes = {}

    def __getitem__(self, index):
        # Return sliced data.
        return self.data.__getitem__(index)
        

class GridType(BaseType):
    def __init__(self):
        self.array = ArrayType()
        self.maps = {}
        self.attributes = {}

    def __getattr__(self, name):
        # Use attributes from array.
        return getattr(self.array, name)

    def _getdata(self):
        return self.array.data

    def _setdata(self, value):
        self.array.data = value
    data = property(_getdata, _setdata)

    def __getitem__(self, index):
        # First we make a copy.
        output = copy.deepcopy(self)

        # Slice the array.
        output.array.data = self.array.__getitem__(index)
        # Ensure that output.array.data in an array.
        if not isinstance(output.array.data, numarray.numarraycore.NumArray):
            output.array.data = numarray.array([output.array.data])    
        output.array.shape = output.array.data.shape

        # Tuplify index.
        if not isinstance(index, tuple):
            index = (index,)

        # Slice the maps.
        for map_, slice_ in zip(self.array.dimensions, index):
            output.maps[map_].data = self.maps[map_].__getitem__(slice_)

        return output

    def add_map(self, name, values):
        self.maps[name] = ArrayType()
        self.maps[name].name = name
        self.maps[name].data = values
        self.maps[name].type = typeconvert[self.maps[name].data.typecode()]
        self.maps[name].dimensions = (name,)
        self.maps[name].shape = self.maps[name].data.shape


class DatasetType(dict):
    pass
