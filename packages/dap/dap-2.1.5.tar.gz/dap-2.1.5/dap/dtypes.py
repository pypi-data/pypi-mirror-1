"""DAP types as Python classes.

This module maps the types defined in the DAP specification to classes.
These classes are used both by the client and the server implementation to
fully represent a dataset.

(Show example of a dataset: DDS, DAS, and building it with the classes.)

All classes have in common a ``data`` property.
"""

__author__ = "Roberto De Almeida <rob@pydap.org>"

import itertools
import copy

from dap.lib import quote
from dap.util.ordereddict import odict


class StructureType(odict):
    """Structure constructor.

    A Structure is a dict-like object that stores other DAP variables.
    """
    def __init__(self, name='', attributes=None):
        """Create a Structure object.

        A simple example:

            >>> from dap import dtypes
            >>> struct = dtypes.StructureType(name='struct', attributes={'foo': 'bar'})
            >>> struct.attributes['foo'] = 'baz'

        Add a ``BaseType`` to it:

            >>> struct['a'] = dtypes.BaseType(name='a', type='Int32')

        And show the DDS and DAS:

            >>> from dap.responses import dds, das
            >>> print ''.join(dds.build(struct))
            Structure {
                Int32 a;
            } struct;
            <BLANKLINE>

            >>> print ''.join(das.build(struct))
            struct {
                String foo "baz";
                a {
                }
            }
            <BLANKLINE>
        """
        super(StructureType, self).__init__(self)
        self.name = quote(name)
        if attributes is None: attributes = {}
        self.attributes = attributes

        self._id = name
        self._data = None

        # Filter for selection expressions.
        self._filters = []

    def __getattr__(self, attr):
        """Try to return attribute from ``self.attributes``."""
        try:
            return self.attributes[attr]
        except KeyError:
            raise AttributeError

    def __setitem__(self, key, item):
        """Modified __setitem__ that propagates id.

        This method sets the id of a variable stored in the structure:

            >>> structure = StructureType(name='foo')
            >>> structure['bar'] = BaseType(name='bar')
            >>> print structure['bar'].id
            foo.bar
        """
        self._dict.__setitem__(key, item)
        if key not in self._keys: self._keys.append(key)

        # Ensure that stored objects have the proper id.
        try:
            item._set_id(self._id)
        except:
            pass

    def _iterdata(self):
        """Method to iterate over the data, in case it's inside a Sequence."""
        return itertools.izip(*self.data)

    def _get_data(self):
        if not self._data:
            # Return list of data from stored vars.
            self._data = [var.data for var in self.values()]
        return self._data

    def _set_data(self, value):
        self._data = value
    data = property(_get_data, _set_data)

    def _get_id(self):
        return self._id

    def _set_id(self, parent):
        """Set own id, and propagate it to stored variables."""
        if parent:
            self._id = '.'.join([parent, self.name])
        else:
            self._id = self.name

        # Propagate id.
        for var in self.values():
            var._set_id(self._id)
    id = property(_get_id)  # Read-only.

    def _get_filters(self):
        return self._filters

    def _set_filters(self, f):
        self._filters.append(f)

        # Propagate filter.
        for var in self.values():
            var._set_filters(f)
    filters = property(_get_filters, _set_filters)

    def filter(self, *filters):
        """Filter a sequence.
        
        This is used for filtering objects inside sequences, according
        to a given constraint expression:

            >>> from dap.client import open
            >>> from dap.responses import dds
            >>> dataset = open("http://www.epic.noaa.gov:10100/dods/epic/race_beringsea_prof_mbt.cdp")
            >>> location = dataset['location']

        Now we can filter the sequence where the latitude is between 59.9
        and 60.0:

            >>> print location['lat'].id
            location.lat
            >>> flocation = location.filter('location.lat>59.9')
            >>> flocation = flocation.filter('location.lat<60')
        """
        # Make a copy of the sequence.
        out = copy.deepcopy(self)

        # And filter it according to the selection expression.
        for filter_ in filters:
            out._set_filters(filter_)
        return out


class DatasetType(StructureType):
    """Dataset constructor.

    The dataset is a special case of a structure. Nothing to see here.
    """
    # Override __setitem__ because we don't want the
    # dataset name when composing the fully qualified
    # name (id).
    def __setitem__(self, key, item):
        """Modified __setitem__ that propagates id.

        This version differs from the StructureType __setitem__ in that the
        dataset id is not used to form the fully qualified name of the
        variables.
        """
        self._dict.__setitem__(key, item)
        if key not in self._keys: self._keys.append(key)

        # Set the id.
        try:
            item._set_id(None)
        except:
            pass


class SequenceType(StructureType):
    """Sequence constructor.

    A Sequence works like a structure, except that the variables that it
    stores have their data changed when the sequence is iterated over.
    """
    def __init__(self, name='', data=None, attributes=None):
        r"""Create a Sequence.

        Sequences contain other DAP variables with iterable data. You
        can think of Sequences as an object holding columns from a
        SQL server. Each variable inside the Sequence corresponds to a
        column, and the data in each variable is an iterable.

        Creating a Sequence:
        
            >>> from dap import dtypes
            >>> seq = dtypes.SequenceType(name='foo')

        Adding variables to it:

            >>> seq['a'] = dtypes.BaseType(name='a', type='Int32')
            >>> seq['b'] = dtypes.BaseType(name='b', type='Int32')

        And adding data to the variables:

            >>> seq['a'].data = range(5)
            >>> seq['b'].data = range(5)

        Let's check the ASCII response for the whole Sequence:

            >>> from dap.responses import ascii
            >>> print ''.join(ascii.build(seq)).strip()
            foo.a, foo.b
            0, 0
            1, 1
            2, 2
            3, 3
            4, 4

        Data can also be accessed individually for each variable:

            >>> for a in seq['a']:
            ...     print a
            0
            1
            2
            3
            4

        Things get complicated with nested sequences, ie, Sequences
        contaning other Sequences. First let's create a Sequence and add
        some variables:

            >>> seq = dtypes.SequenceType(name='foo')
            >>> seq['a'] = dtypes.BaseType(name='a', type='Int32')
            >>> seq['b'] = dtypes.BaseType(name='b', type='Int32')
            >>> seq['c'] = dtypes.SequenceType(name='c')

        Notice that we added a Sequence ``c`` to the original Sequence.
        Now let's add variables to *this* Sequence:

            >>> seq['c']['d'] = dtypes.BaseType(name='d')
            >>> seq['c']['e'] = dtypes.BaseType(name='e')
            >>> seq['c']['f'] = dtypes.BaseType(name='f')

        We add the data to all variables:

            >>> seq['a'].data = range(5)
            >>> seq['b'].data = range(5)
            >>> seq['c']['d'].data = [[0]] * 5
            >>> seq['c']['e'].data = [[1]] * 5
            >>> seq['c']['f'].data = [[2]] * 5

        Here's the data we just added:

            >>> print list(seq.data)
            [(0, 0, ([0], [1], [2])), (1, 1, ([0], [1], [2])), (2, 2, ([0], [1], [2])), (3, 3, ([0], [1], [2])), (4, 4, ([0], [1], [2]))]
            >>> print list(seq['c'].data)
            [([0], [1], [2]), ([0], [1], [2]), ([0], [1], [2]), ([0], [1], [2]), ([0], [1], [2])]

        And here's the ASCII response:

            >>> print ''.join(ascii.build(seq)).strip().replace('\n\n', '\n<BLANKLINE>\n')  # hack for Python < 2.4
            foo.a, foo.b, foo.c
            0, 0, foo.c.d, foo.c.e, foo.c.f
            0, 1, 2
            <BLANKLINE>
            1, 1, foo.c.d, foo.c.e, foo.c.f
            0, 1, 2
            <BLANKLINE>
            2, 2, foo.c.d, foo.c.e, foo.c.f
            0, 1, 2
            <BLANKLINE>
            3, 3, foo.c.d, foo.c.e, foo.c.f
            0, 1, 2
            <BLANKLINE>
            4, 4, foo.c.d, foo.c.e, foo.c.f
            0, 1, 2

        (Nested sequences are the root of all evil. At least 80% of the time
        spent developing this module was because of them. What happened to the
        good ol' arrays?)
        """
        # I need to read more about super(). Why doesn't this work?
        #super(SequenceType, self).__init__(self, name, attributes)
        StructureType.__init__(self, name, attributes)
        if data is None: data = []
        self._data = data

    def _iterdata(self):
        # Iterate over the data.
        return iter(self.data)

    def _get_data(self):
        if self._data:
            return self._data
        else:
            # Iterate over the objects stored in the Sequence.
            data = [var._iterdata() for var in self.values()]
            return itertools.izip(*data)

    def _set_data(self, value):
        self._data = value
    data = property(_get_data, _set_data)


class BaseType(object):
    """Base DAP type constructor.

    This is the basic DAP type holding a single value.
    """
    def __init__(self, data=None, name='', type=None, attributes=None):
        """Create a basic DAP variable.

        This is the basic data type in the DAP. A ``BaseType`` object
        contains a single value:

            >>> from dap import dtypes
            >>> dataset = dtypes.DatasetType(name='SimpleTypes')
            >>> dataset['b'] = dtypes.BaseType(data=0, name='b', type='Byte')
            >>> dataset['i32'] = dtypes.BaseType(data=1, name='i32', type='Int32')
            >>> dataset['ui32'] = dtypes.BaseType(data=0, name='ui32', type='UInt32')
            >>> dataset['i16'] = dtypes.BaseType(data=0, name='i16', type='Int16')
            >>> dataset['ui16'] = dtypes.BaseType(data=0, name='ui16', type='UInt16')
            >>> dataset['f32'] = dtypes.BaseType(data=0.0, name='f32', type='Float32')
            >>> dataset['f64'] = dtypes.BaseType(data=1000.0, name='f64', type='Float64')
            >>> dataset['s'] = dtypes.BaseType(data="This is a data test string (pass 0).", name='s', type='String')
            >>> dataset['u'] = dtypes.BaseType(data="http://www.dods.org", name='u', type='Url')

        Here's the ASCII representation of the dataset above:

            >>> from dap.responses import ascii
            >>> print ''.join(ascii.build(dataset)).strip()
            b, 0
            i32, 1
            ui32, 0
            i16, 0
            ui16, 0
            f32, 0
            f64, 1000
            s, "This is a data test string (pass 0)."
            u, "http://www.dods.org"
        """
        self.data = data
        self.name = quote(name)
        self.type = type
        if attributes is None: attributes = {}
        self.attributes = attributes

        self._id = name

        # Filter for selection expressions.
        self._filters = []

    def __getattr__(self, attr):
        try:
            return self.attributes[attr]
        except KeyError:
            raise AttributeError

    def _iterdata(self):
        # Iterate over the data.
        return iter(self.data)

    def __getitem__(self, index):
        try:
            return self.data[index]
        except TypeError:
            return self.data

    def _get_id(self):
        return self._id

    def _set_id(self, parent):
        if parent:
            self._id = '.'.join([parent, self.name])
        else:
            self._id = self.name
    id = property(_get_id)  # Read-only.

    def _get_filters(self):
        return self._filters

    def _set_filters(self, f):
        self._filters.append(f)
    filters = property(_get_filters, _set_filters)


class ArrayType(BaseType):
    """Array constructor.

    An Array is a constructor variable holding multidimensional data.
    PyDAP supports only Arrays of base types (integers, floats or
    strings) for now. Support for Arrays containing *other* constructor
    variables, eg, an Array of Sequences, is planned for the future.
    """
    def __init__(self, data=None, name='', dimensions=None, shape=None, type=None, attributes=None):
        """Create an Array.

        An Array can hold multidimensional data:

            >>> from dap import array
            >>> data = array([1,2,3,4])
            >>> data.shape = (2,2)

        The object ``data`` should be iterable value by value, which is
        not true for Numeric/numarray/scipy_core arrays. Here's how we
        fix that:

            >>> from dap.util.arrayterator import arrayterator
            >>> data = arrayterator(data)

        Now we create the array:
            
            >>> from dap import dtypes
            >>> array = dtypes.ArrayType(data=data, name='array', shape=(2,2), type='Int32')
            >>> print array.data
            [[1 2]
             [3 4]]

        Here's the ASCII representation:

            >>> from dap.responses import ascii
            >>> print ''.join(ascii.build(array))
            array[2][2]
            [0], 1, 2
            [1], 3, 4
        """
        self.data = data
        self.name = quote(name)
        self.dimensions = dimensions
        if shape is None: shape = []
        self._shape = shape
        self.type = type
        if attributes is None: attributes = {}
        self.attributes = attributes

        self._id = name

        # Filter for selection expressions.
        self._filters = []

    def __len__(self):
        return len(self.data)

    def __getitem__(self, index):
        return self.data[index]

    def __deepcopy__(self, memo):
        out = self.__class__(data=None, name=self.name, dimensions=self.dimensions, shape=self.shape, type=self.type, attributes=self.attributes)
        out.data = copy.copy(self.data)
        return out

    def _set_shape(self, value):
        self._shape = value

    def _get_shape(self):
        if self._shape:
            return self._shape
        else:
            return getattr(self.data, 'shape', [])
    shape = property(_get_shape, _set_shape)


class GridType(ArrayType):
    """Grid constructor.

    A Grid is a variable whose dimensions are indexed by Array
    variables.
    """
    def __init__(self, data=None, name='', dimensions=None, shape=None, type=None, attributes=None):
        """Create a Grid.

        When creating a Grid, we should specify the dimensions. Here's a
        simple example:
        
            >>> from dap import dtypes, array
            >>> from dap.util.arrayterator import arrayterator

        Create the data:

            >>> data = array([1,2,3,4,5,6])
            >>> data.shape = (2,3)
            >>> data = arrayterator(data)

        And create the grid:

            >>> grid = dtypes.GridType(data=data, name='grid', dimensions=['x', 'y'], shape=[2,3], type='Int32')
            >>> grid.maps['x'] = dtypes.ArrayType(data=array([1,2]), name='x', shape=[2], type='Int32')
            >>> grid.maps['y'] = dtypes.ArrayType(data=array([1,2,3]), name='y', shape=[3], type='Int32')

        Here's its ASCII representation:

            >>> from dap.responses import ascii
            >>> print ''.join(ascii.build(grid)).strip()
            grid[2][3]
            [0], 1, 2, 3
            [1], 4, 5, 6
            <BLANKLINE>
            y[3]
            1, 2, 3
            <BLANKLINE>
            x[2]
            1, 2
        """
        self.array = ArrayType(data, name=name, dimensions=dimensions, shape=shape, type=type)
        self.name = quote(name)
        self.dimensions = dimensions
        if shape is None: shape = []
        self._shape = shape
        self.type = type
        if attributes is None: attributes = {}
        self.attributes = attributes

        self.maps = {}

        self._id = name

        # Filter for selection expressions.
        self._filters = []

    def __deepcopy__(self, memo):
        out = self.__class__(data=None, name=self.name, dimensions=self.dimensions, shape=self.shape, type=self.type, attributes=self.attributes)
        out.data = copy.copy(self.data)
        out.maps = copy.deepcopy(self.maps)
        return out

    def _set_id(self, parent):
        """Set own id, and propagate it to stored variables."""
        if parent:
            self._id = '.'.join([parent, self.name])
        else:
            self._id = self.name

        # Propagate id.
        self.array._set_id(self._id)
        for var in self.maps.values():
            var._set_id(self._id)

    def _get_filters(self):
        return self._filters

    def _set_filters(self, f):
        self._filters.append(f)

        # Propagate filter.
        self.array._set_filter(f)
        for var in self.maps():
            var._set_filters(f)
    filters = property(_get_filters, _set_filters)

    def _set_type(self, value):
        self.array.type = value

    def _get_type(self):
        return self.array.type
    type = property(_get_type, _set_type)

    def _get_data(self):
        return self.array.data

    def _set_data(self, value):
        self.array.data = value
    data = property(_get_data, _set_data)

    def _set_shape(self, value):
        self.array.shape = self._shape = value

    def _get_shape(self):
        if self._shape:
            return self._shape
        else:
            return getattr(self.array, 'shape', [])
    shape = property(_get_shape, _set_shape)


def _test():
    import doctest
    doctest.testmod()

if __name__ == "__main__":
    _test()
