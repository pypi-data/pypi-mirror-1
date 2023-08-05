"""ASCII DAP response.

This module implements the ASCII DAP response, building it 
dynamically from datasets objects.
"""

__author__ = "Roberto De Almeida <rob@pydap.org>"

import itertools

from dap import dtypes, INDENT
from dap.lib import encode_atom, isiterable


def n_iterate(t):
    """Iterator over n-tuple.

    This function is used when representing data in the ASCII response. It
    iterates over a n-dimensional tuple/list, yielding all indexes in
    order.

        >>> for l in n_iterate([1,2,3]):
        ...     print l
        [0, 0, 0]
        [0, 0, 1]
        [0, 0, 2]
        [0, 1, 0]
        [0, 1, 1]
        [0, 1, 2]

    [http://dealmeida.net/en/Programming/Python/multi-dimensional_iteration]
    """
    if not t:
        yield []
        raise StopIteration

    output = [0] * len(t)

    # Check if any length is zero.
    if 0 in t: raise StopIteration

    while 1:
        # Check digits from right to left.
        for i in range(len(t)-1,0,-1):
            if output[i] >= t[i]:
                # Carry numbers to the left.
                output[i] = 0
                output[i-1] += 1
            else:
                break

        if output[0] >= t[0]: raise StopIteration

        yield output

        # Add 1.
        output[-1] += 1


def build(dapvar, data=None, printname=True):
    """Build ASCII response.

        >>> dataset = dtypes.DatasetType(name='NestedSequences')
        >>> seq = dataset['person1'] = dtypes.SequenceType(name='person1')
        >>> seq['age'] = dtypes.BaseType(name='age', type='Int32', data=[1,2,3,5,8])
        >>> seq['stuff'] = dtypes.SequenceType(name='stuff')
        >>> seq['stuff']['foo'] = dtypes.BaseType(name='foo', type='Int16',data=[[i*80 + j*16 for j in range(5)] for i in range(5)])
        >>> print ''.join(build(dataset))
        person1.age, person1.stuff
        1, person1.stuff.foo
        0
        16
        32
        48
        64
        <BLANKLINE>
        2, person1.stuff.foo
        80
        96
        112
        128
        144
        <BLANKLINE>
        3, person1.stuff.foo
        160
        176
        192
        208
        224
        <BLANKLINE>
        5, person1.stuff.foo
        240
        256
        272
        288
        304
        <BLANKLINE>
        8, person1.stuff.foo
        320
        336
        352
        368
        384
        <BLANKLINE>
        <BLANKLINE>
        <BLANKLINE>

    Testing with infinite sequences:

        >>> dataset = dtypes.DatasetType(name='infinite')
        >>> seq = dataset['sequences'] = dtypes.SequenceType(name='sequences')
        >>> integers = seq['integers'] = dtypes.BaseType(name='integers', type='Int32')
        >>> integers.data = range(10)
        >>> even = seq['even'] = dtypes.BaseType(name='even', type='Int32')
        >>> even.data = itertools.imap(lambda x: x*2, range(10))
        >>> print ''.join(build(dataset))
        sequences.integers, sequences.even
        0, 0
        1, 2
        2, 4
        3, 6
        4, 8
        5, 10
        6, 12
        7, 14
        8, 16
        9, 18
        <BLANKLINE>
        <BLANKLINE>
        >>> integers.data = itertools.count()
        >>> even.data = itertools.imap(lambda x: x*2, itertools.count())
        >>> for i,line in enumerate(build(dataset)):
        ...     if i > 10: break
        ...     print line,
        sequences.integers, sequences.even
        0, 0 
        1, 2 
        2, 4 
        3, 6 
        4, 8 
    """
    func = {dtypes.DatasetType  : _dataset,
            dtypes.StructureType: _structure,
            dtypes.SequenceType : _sequence,
            dtypes.BaseType     : _base,
            dtypes.ArrayType    : _array,
            dtypes.GridType     : _grid,
           }[type(dapvar)]

    return func(dapvar, data, printname)


def _dataset(dapvar, data=None, printname=True):
    for var in dapvar.values():
        for ascii_ in build(var, printname=printname):
            yield ascii_
        yield '\n'


def _structure(dapvar, data=None, printname=True):
    if data is None: 
        for var in dapvar.values():
            for ascii_ in build(var, printname=printname):
                yield ascii_
            yield '\n'
    
    # Inside a Sequence.
    else:
        # Make data iterable.
        if not isiterable(data): data = [data]
    
        # Propagate data.
        for var,vardata in itertools.izip(dapvar.values(), data):
            # Check for sequences.
            if isinstance(var, dtypes.SequenceType):
                vardata = itertools.izip(*vardata)

            for ascii_ in build(var, data=vardata):
                yield ascii_
            yield '\n'


def _sequence(dapvar, data=None, printname=True):
    if data is None: data = dapvar.data

    yield '%s\n' % ', '.join([var.id for var in dapvar.values()])

    for data_ in data:
        line = []

        # Make data iterable.
        if not isiterable(data_): data_ = [data_]

        # Propagate data.
        for var,vardata in itertools.izip(dapvar.values(), data_):
            # Check for sequences.
            if isinstance(var, dtypes.SequenceType):
                vardata = itertools.izip(*vardata)

            tmp = []
            for ascii_ in build(var, data=vardata, printname=False):
                tmp.append(ascii_)
            line.append(''.join(tmp))

        yield ', '.join(line)
        yield '\n'


def _base(dapvar, data=None, printname=True):
    if data is None: data = dapvar.data
    if printname: yield '%s, ' % dapvar.name
    yield '%s' % encode_atom(data)


def _array(dapvar, data=None, printname=True):
    if data is None: data = dapvar.data

    shape =  ']['.join([str(i) for i in dapvar.shape])
    shape = '[%s]' % shape
    yield '%s%s\n' % (dapvar.name, shape)

    i = n_iterate(dapvar.shape[:-1])
    for line,j in enumerate(data):
        if (line % dapvar.shape[-1]) == 0:
            if line: yield '\n'
            dims = i.next()
            if dims:
                for dim in dims:
                    yield '[%d]' % dim
                yield ', '
        else:
            yield ', '
        try:
            yield '%s' % encode_atom(j[0])
        except TypeError:
            yield '%s' % encode_atom(j)


def _grid(dapvar, data=None, printname=True):
    for ascii_ in build(dapvar.array, data=data, printname=printname):
        yield ascii_
    yield '\n\n'
    for map_ in dapvar.maps.values():
        for ascii_ in build(map_, data=None, printname=printname):
            yield ascii_
        yield '\n\n'


def _test():
    import doctest
    doctest.testmod()

if __name__ == "__main__":
    _test()

