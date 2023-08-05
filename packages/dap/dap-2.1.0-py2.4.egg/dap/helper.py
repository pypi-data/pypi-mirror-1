"""Helper functions.

These are generic functions used mostly for writing plugins.
"""

__author__ = "Roberto De Almeida <rob@pydap.org>"

import re
import urllib
import operator
import itertools
import copy as copy_
from urllib import quote
from urlparse import urlsplit

from dap import dtypes
from dap.exceptions import ConstraintExpressionError
from dap.lib import isiterable
from dap.util.safeeval import expr_eval


# Conversion between numarray/Numpy types and the DAP types.
typecode_to_dap = {'d': 'Float64',
                   'f': 'Float32',
                   'l': 'Int32',
                   'i': 'Int32',
                   's': 'Int16',
                   '1': 'Byte',
                   'b': 'Uint16',
                   'c': 'String',
                  }


def trim(dataset, constraints, copy=True):
    """Trim a dataset according to a selection.

    This function can be used when writing plugins to parse a constraint
    expression and produce the desired dataset. Given a dataset object
    representing the *full* dataset and a CE, the function will return
    a "trimmed" dataset.
    
    A simple example. We create a dataset holding three variables:

        >>> dataset = dtypes.DatasetType(name='foo')
        >>> dataset['a'] = dtypes.BaseType(name='a', type='Byte')
        >>> dataset['b'] = dtypes.BaseType(name='b', type='Byte')
        >>> dataset['c'] = dtypes.BaseType(name='c', type='Byte')

    Now we give it a CE requesting only the variables ``a`` and ``b``: 
    
        >>> dataset2 = trim(dataset, 'a,b')
        >>> print dataset2  #doctest: +ELLIPSIS
        {'a': <dap.dtypes.BaseType object at ...>, 'b': <dap.dtypes.BaseType object at ...>}

    Another example. A dataset with two structures ``a`` and ``b``:

        >>> dataset = dtypes.DatasetType(name='foo')
        >>> dataset['a'] = dtypes.StructureType(name='a')
        >>> dataset['a']['a1'] = dtypes.BaseType(name='a1', type='Byte')
        >>> dataset['b'] = dtypes.StructureType(name='b')
        >>> dataset['b']['b1'] = dtypes.BaseType(name='b1', type='Byte')
        >>> dataset['b']['b2'] = dtypes.BaseType(name='b2', type='Byte')

    If we request the structure ``b`` we should get it complete:
    
        >>> dataset2 = trim(dataset, 'a.a1,b')
        >>> print dataset2  #doctest: +ELLIPSIS
        {'a': {'a1': <dap.dtypes.BaseType object at ...>}, 'b': {'b1': <dap.dtypes.BaseType object at ...>, 'b2': <dap.dtypes.BaseType object at ...>}}

        >>> dataset2 = trim(dataset, 'a.a1')
        >>> print dataset2  #doctest: +ELLIPSIS
        {'a': {'a1': <dap.dtypes.BaseType object at ...>}}

    Arrays can be sliced. Here we have a ``(2,3)`` array:

        >>> dataset = dtypes.DatasetType(name='foo')
        >>> from numarray import array
        >>> dataset['array'] = dtypes.ArrayType(data=array([1,2,3,4,5,6], shape=(2,3)), name='array', shape=[2,3], type='Int32')
        >>> dataset2 = trim(dataset, 'array')
        >>> from dap.responses import dds, ascii
        >>> print ''.join(dds.build(dataset2)).strip()
        Dataset {
            Int32 array[2][3];
        } foo;
        >>> print dataset2['array'].data
        [[1 2 3]
         [4 5 6]]

    But we request only part of it:

        >>> dataset2 = trim(dataset, 'array[0:1:1][0:1:1]')
        >>> print ''.join(dds.build(dataset2)).strip()
        Dataset {
            Int32 array[2][2];
        } foo;
        >>> print dataset2['array'].data
        [[1 2]
         [4 5]]

    The same is valid for grids:

        >>> dataset['grid'] = dtypes.GridType(data=array([1,2,3,4,5,6], shape=(2,3)), name='grid', dimensions=['x', 'y'], shape=[2,3], type='Int32')
        >>> dataset['grid'].maps['x'] = dtypes.ArrayType(data=array([1,2]), name='x', shape=[2], type='Int32')
        >>> dataset['grid'].maps['y'] = dtypes.ArrayType(data=array([1,2,3]), name='y', shape=[3], type='Int32')
        >>> print ''.join(dds.build(dataset)).strip()
        Dataset {
            Int32 array[2][3];
            Grid {
                Array:
                    Int32 grid[x = 2][y = 3];
                Maps:
                    Int32 y[y = 3];
                    Int32 x[x = 2];
            } grid;
        } foo;
        
        >>> dataset2 = trim(dataset, 'grid[0:1:0][0:1:0]')
        >>> print ''.join(dds.build(dataset2)).strip()
        Dataset {
            Grid {
                Array:
                    Int32 grid[x = 1][y = 1];
                Maps:
                    Int32 y[y = 1];
                    Int32 x[x = 1];
            } grid;
        } foo;
        >>> print ''.join(ascii.build(dataset2)).strip()
        grid[1][1]
        [0], 1
        <BLANKLINE>
        y[1]
        1
        <BLANKLINE>
        x[1]
        1

    It also works with Sequences:

        >>> dataset = dtypes.DatasetType(name='foo')
        >>> dataset['seq'] = dtypes.SequenceType(name='seq')
        >>> dataset['seq']['a'] = dtypes.BaseType(name='a', type='Int32')
        >>> dataset['seq']['b'] = dtypes.BaseType(name='b', type='Int32')
        >>> dataset['seq']['a'].data = range(5)
        >>> dataset['seq']['b'].data = range(5)
        >>> for i in dataset['seq'].data:
        ...     print i
        (0, 0)
        (1, 1)
        (2, 2)
        (3, 3)
        (4, 4)
        >>> dataset2 = trim(dataset, 'seq.a')
        >>> for i in dataset2['seq'].data:
        ...     print i
        (0,)
        (1,)
        (2,)
        (3,)
        (4,)

    The function also parses selection expressions. Let's create a
    dataset with sequential data:

        >>> dataset = dtypes.DatasetType(name='foo')
        >>> dataset['seq'] = dtypes.SequenceType(name='seq')
        >>> dataset['seq']['index'] = dtypes.BaseType(name='index', type='Int32')
        >>> dataset['seq']['index'].data = [10, 11, 12, 13]
        >>> dataset['seq']['temperature'] = dtypes.BaseType(name='temperature', type='Float32')
        >>> dataset['seq']['temperature'].data = [17.2, 15.1, 15.3, 15.1]
        >>> dataset['seq']['site'] = dtypes.BaseType(name='site', type='String')
        >>> dataset['seq']['site'].data = ['Diamond_St', 'Blacktail_Loop', 'Platinum_St', 'Kodiak_Trail']

    Here's the data:
    
        >>> for i in dataset['seq'].data:
        ...     print i
        (10, 17.199999999999999, 'Diamond_St')
        (11, 15.1, 'Blacktail_Loop')
        (12, 15.300000000000001, 'Platinum_St')
        (13, 15.1, 'Kodiak_Trail')

    Now suppose we only want data where ``index`` is greater than 11:
        
        >>> dataset2 = trim(dataset, 'seq&seq.index>11')
        >>> for i in dataset2['seq'].data:
        ...     print i
        (12, 15.300000000000001, 'Platinum_St')
        (13, 15.1, 'Kodiak_Trail')

    We can request only a few variables:
        
        >>> dataset2 = trim(dataset, 'seq.site&seq.index>11')
        >>> for i in dataset2['seq'].data:
        ...     print i
        ['Platinum_St']
        ['Kodiak_Trail']
    """
    #if constraints is None: return dataset
    if not constraints: return dataset

    # Work with a copy? (default)
    if copy: dataset = copy_.deepcopy(dataset)

    constraints = urllib.unquote(constraints)
    constraints = constraints.split('&')

    # Selection expression.
    queries = constraints[1:]

    # Requested vars.
    vars_ = constraints[0]
    vars_ = vars_.split(',')

    # First we need to collect all variables requested.
    fields = {}
    for var in vars_:
        if var:
            # Check if the var has a slice.
            p = re.compile(r'(?P<name>[^[]+)(?P<shape>(\[[^\]]+\])*)')
            c = p.match(var).groupdict()
            id_ = c['name']
            fields[id_] = c['shape']

    # Apply selection expression.
    if queries:
        def filter(dapvar):
            for k,v in dapvar.items():
                if isinstance(v, dtypes.SequenceType):
                    # Get only related queries.
                    queries_ = [q for q in queries if q.startswith(v.id)]
                    if queries_:
                        ids = [var.id for var in v.values()]
                        f = getfilter(queries_, ids)
                        data = itertools.ifilter(f, v.data)

                        # Get selected variables.
                        seqvars = [var for var in vars_ if var.startswith('%s.' % v.id)]
                        if seqvars:
                            indexes = [ids.index(n) for n in seqvars]
                            filter_ = lambda x: [x[i] for i in indexes]
                            data = itertools.imap(filter_, data)
                        
                        v.data = data

                elif isinstance(v, dtypes.StructureType):
                    filter(v)
        filter(dataset)
        
    # Remove variables not in request.
    def strip(dapvar):
        # If Structure id in fields, leave everything.
        if not dapvar.id in fields.keys():
            for k,v in dapvar.items():
                if isinstance(v, dtypes.BaseType):
                    if v.id not in fields.keys():
                        del dapvar[k]
                    else:
                        # Apply stride?
                        slice_ = fields[v.id]
                        if slice_:
                            slice_ = getslice(slice_, v.shape)
                            v.data = v.data[slice_]
                            v.shape = v.data.shape  # unnecessary?

                            # Check for grids.
                            if isinstance(v, dtypes.GridType):
                                # Tuplify slice_.
                                if not isiterable(slice_):
                                    slice_ = (slice_,)

                                # Slice the maps.
                                for map_,mapslice in zip(v.maps.values(), slice_):
                                    map_.data = map_.data[mapslice]
                                    map_.shape = map_.data.shape
                else:
                    strip(v)
                    if not v.keys():
                        del dapvar[k]

    # Strip the dataset of everything that doesn't belong.
    strip(dataset)

    return dataset
                

def getslice(hyperslab, shape):
    """Parse a hyperslab.

    Parse a hyperslab to a slice according to variable shape. The hyperslab
    follows the DAP specification, and ommited dimensions are returned in 
    their entirety.

        >>> getslice('[0:1:2][0:1:2]', [3,3])
        [slice(0, 3, 1), slice(0, 3, 1)]
        >>> getslice('[0:2][0:2]', [3,3])
        [slice(0, 3, 1), slice(0, 3, 1)]
        >>> getslice('[0][2]', [3,3])
        [slice(0, 1, 1), slice(2, 3, 1)]
        >>> getslice('[0:1:1]', [3,3])
        [slice(0, 2, 1), slice(0, 3, 1)]
        >>> getslice('[0:2:1]', [3,3])
        [slice(0, 2, 2), slice(0, 3, 1)]
        >>> getslice('', [3,3])
        [slice(0, 3, 1), slice(0, 3, 1)]
    """
    output = []
    dimslices = []

    if hyperslab:
        dimslices = hyperslab[1:-1].split('][')
        for dimslice in dimslices:
            start, size, step = _getsize(dimslice)
            output.append(slice(start, start+size, step))

    # Pad unnamed dimensions.
    if len(dimslices) < len(shape):
        for size in shape[len(dimslices):]:
            output.append(slice(0, size, 1))

    if len(output) > len(shape):
        raise ConstraintExpressionError, 'Hyperslab %s has more dimensions than variable shape %s.' % (hyperslab, str(shape))

    return output


def _getsize(dimslice):
    """Parse a dimension from a hyperslab.

    Calculates the start, size and step from a DAP formatted hyperslab.

        >>> _getsize('0:1:9')
        (0, 10, 1)
        >>> _getsize('0:2:9')
        (0, 10, 2)
        >>> _getsize('0')
        (0, 1, 1)
        >>> _getsize('0:9')
        (0, 10, 1)
    """
    size = dimslice.split(':')

    start = int(size[0])
    if len(size) == 1:
        stop = start
        step = 1
    elif len(size) == 2:
        stop = int(size[1])
        step = 1
    elif len(size) == 3:
        step = int(size[1])
        stop = int(size[2])
    else:
        raise ConstraintExpressionError, 'Invalid hyperslab: %s.' % dimslice
    size = (stop-start) + 1
    
    return start, size, step


def getfilter(queries, vars_):
    """This function is a filter builder.

    Given a list of DAP formatted queries and a list of variable names,
    this function returns a dynamic filter function to filter rows.

    From the example in the DAP specification:

        >>> vars_ = ['index', 'temperature', 'site']
        >>> data = []
        >>> data.append([10, 17.2, 'Diamond_St'])
        >>> data.append([11, 15.1, 'Blacktail_Loop'])
        >>> data.append([12, 15.3, 'Platinum_St'])
        >>> data.append([13, 15.1, 'Kodiak_Trail'])

    Rows where index is greater-than-or-equal 11:

        >>> f = getfilter(['index>=11'], vars_)
        >>> for line in itertools.ifilter(f, data):
        ...     print line
        [11, 15.1, 'Blacktail_Loop']
        [12, 15.300000000000001, 'Platinum_St']
        [13, 15.1, 'Kodiak_Trail']

    Rows where site ends with '_St':

        >>> f = getfilter(['site=~".*_St"'], vars_)
        >>> for line in itertools.ifilter(f, data):
        ...     print line
        [10, 17.199999999999999, 'Diamond_St']
        [12, 15.300000000000001, 'Platinum_St']

    Index greater-or-equal-than 11 AND site ends with '_St':

        >>> f = getfilter(['site=~".*_St"', 'index>=11'], vars_)
        >>> for line in itertools.ifilter(f, data):
        ...     print line
        [12, 15.300000000000001, 'Platinum_St']

    Site is either 'Diamond_St' OR 'Blacktail_Loop':
    
        >>> f = getfilter(['site={"Diamond_St", "Blacktail_Loop"}'], vars_)
        >>> for line in itertools.ifilter(f, data):
        ...     print line
        [10, 17.199999999999999, 'Diamond_St']
        [11, 15.1, 'Blacktail_Loop']

    Index is either 10 OR 12:

        >>> f = getfilter(['index={10, 12}'], vars_)
        >>> for line in itertools.ifilter(f, data):
        ...     print line
        [10, 17.199999999999999, 'Diamond_St']
        [12, 15.300000000000001, 'Platinum_St']

    Python is great, isn't it? :)
    """
    filters = []
    p = re.compile(r'''^                          # Start of selection
                       {?                         # Optional { for multi-valued constants
                       (?P<var1>.*?)              # Anything
                       }?                         # Closing }
                       (?P<op><=|>=|!=|=~|>|<|=)  # Operators
                       {?                         # {
                       (?P<var2>.*?)              # Anything
                       }?                         # }
                       $                          # EOL
                    ''', re.VERBOSE)
    for query in queries:
        m = p.match(query)
        if not m: raise ConstraintExpressionError, 'Invalid constraint expression: %s.' % query

        # Functions associated with each operator.
        op = {'<' : operator.lt,
              '>' : operator.gt,
              '!=': operator.ne,
              '=' : operator.eq,
              '>=': operator.ge,
              '<=': operator.le,
              '=~': lambda a,b: re.match(b,a),
             }[m.group('op')]
        # Allow multiple comparisons in one line. Python rulez!
        op = multicomp(op)

        # Build the filter for the first variable. If it is a known name,
        # the filter is a function that returns the element from the
        # variable column. Otherwise, it's a bogus function that returns
        # always a constant.
        if m.group('var1') in vars_:
            i = vars_.index(m.group('var1'))
            var1 = lambda L, i=i: operator.getitem(L, i)
        else:
            try:
                # Could be a constant.
                var1 = lambda x, m=m: expr_eval(m.group('var1'))
            except:
                raise ConstraintExpressionError, 'Invalid constraint expression: %s.' % query

        # Build the filter for the second variable.
        if m.group('var2') in vars_:
            i = vars_.index(m.group('var2'))
            var2 = lambda L, i=i: operator.getitem(L, i)
        else:
            try:
                # Could be a constant.
                var2 = lambda x, m=m: expr_eval(m.group('var2'))
            except:
                raise ConstraintExpressionError, 'Invalid constraint expression: %s.' % query

        # This is the filter. We apply the function (op) to the variable
        # filters (var1 and var2).
        filter_ = lambda x, op=op, var1=var1, var2=var2: op(var1(x), var2(x))
        filters.append(filter_)

    if filters:
        # We have to join all the filters that were built, using the AND 
        # operator. Believe me, this line does exactly that.
        #
        # You are not expected to understand this.
        filter_ = lambda i: reduce(lambda x,y: x and y, [f(i) for f in filters])
    else:
        filter_ = bool

    return filter_


def multicomp(function):
    """Multiple OR comparisons.

    Given f(a,b), this function returns a new function g(a,b) which
    performs multiple OR comparisons if b is a tuple.

        >>> a = 1
        >>> b = (0, 1, 2)
        >>> operator.lt = multicomp(operator.lt)
        >>> operator.lt(a, b)
        True
    """
    def f(a, b):
        if isinstance(b, tuple):
            for i in b:
                # Return True if any comparison is True.
                if function(a, i): return True
            return False
        else:
            return function(a, b)

    return f


def construct_url(environ, with_query_string=True):
    """Reconstructs the URL from the WSGI environment.
    """
    url = environ['wsgi.url_scheme']+'://'

    if environ.get('HTTP_HOST'):
        url += environ['HTTP_HOST']
    else:
        url += environ['SERVER_NAME']

        if environ['wsgi.url_scheme'] == 'https':
            if environ['SERVER_PORT'] != '443':
                url += ':' + environ['SERVER_PORT']
        else:
            if environ['SERVER_PORT'] != '80':
                url += ':' + environ['SERVER_PORT']

    # Avoid double slash.
    if environ.get('SCRIPT_NAME','') != '/':
        url += quote(environ.get('SCRIPT_NAME',''))

    url += quote(environ.get('PATH_INFO',''))
    if with_query_string:
        if environ.get('QUERY_STRING'):
            url += '?' + environ['QUERY_STRING']
    return url


def linkify(location):
    """Linkify a path location.
    
    Converts a URL into a clickable URL, with each part pointing to the
    corresponding location.

        >>> print linkify("http://example.com/foo/bar")
        <a href="http://example.com">http://example.com</a>/<a href="http://example.com/foo">foo</a>/bar
    """
    # Linkify location.
    scheme, netloc, path = urlsplit(location)[:3]
    base = scheme + '://' + netloc

    # Get names.
    names = [base]
    names.extend(path.split('/')[1:])  # ignore leading /

    # And linkify them.
    links = []
    for i,name in enumerate(names[:-1]):  # don't make a link for the last name
        links.append('/'.join(names[:i+1]))
    links = ['<a href="%s">%s</a>' % (link, name) for link, name in zip(links, names)]
    links.append(names[-1])
    location = '/'.join(links)
    return location


def fix_slice(dims, index):
    """Fix incomplete slices or slices with ellipsis.

    The behaviour of this function was reversed-engineered from numarray.

        >>> fix_slice(3, (0, Ellipsis, 0))
        (0, slice(None, None, None), 0)
        >>> fix_slice(4, (0, Ellipsis, 0))
        (0, slice(None, None, None), slice(None, None, None), 0)
        >>> fix_slice(4, (0, 0, Ellipsis, 0))
        (0, 0, slice(None, None, None), 0)
        >>> fix_slice(5, (0, Ellipsis, 0))
        (0, slice(None, None, None), slice(None, None, None), slice(None, None, None), 0)
        >>> fix_slice(5, (0, 0, Ellipsis, 0))
        (0, 0, slice(None, None, None), slice(None, None, None), 0)
        >>> fix_slice(5, (0, Ellipsis, 0, Ellipsis))
        (0, slice(None, None, None), slice(None, None, None), 0, slice(None, None, None))
        >>> fix_slice(4, slice(None, None, None))
        (slice(None, None, None), slice(None, None, None), slice(None, None, None), slice(None, None, None))
        >>> fix_slice(4, (slice(None, None, None), 0))
        (slice(None, None, None), 0, slice(None, None, None), slice(None, None, None))
    """
    if not isinstance(index, tuple): index = (index,)

    out = []
    length = len(index)
    for i, s in enumerate(index):
        if s is Ellipsis:
            s = [slice(None, None, None)] * (dims - length + 1)
            out.extend(s)
            length += (dims - length)
        else:
            out.append(s)

    if length < dims:
        s = [slice(None, None, None)] * (dims - length)
        out.extend(s)

    return tuple(out)


def _test():
    import doctest
    doctest.testmod()

if __name__ == "__main__":
    _test()
