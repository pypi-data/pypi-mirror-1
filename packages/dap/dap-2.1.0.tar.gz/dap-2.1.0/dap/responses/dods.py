"""DODS DAP response.

This module implements the DODS DAP response, building it
dynamically from datasets objects.
"""

__author__ = "Roberto De Almeida <rob@pydap.org>"

import itertools

from dap import dtypes
from dap.lib import isiterable
from dap.xdr import DapPacker


def build(dapvar, data=None):
    r"""Build a DODS from a DAP object.
        
        >>> dataset = dtypes.DatasetType(name='temp.dat')
        >>> dataset['Tmp'] = dtypes.ArrayType(name='Tmp', shape=[5], type='Int32', data=range(5))
        >>> for line in build(dataset):
        ...     print repr(line)
        '\x00\x00\x00\x05\x00\x00\x00\x05'
        '\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x02\x00\x00\x00\x03\x00\x00\x00\x04'

        >>> import urllib

        >>> dataset = dtypes.DatasetType(name='NestedSequences')
        >>> seq = dataset['person1'] = dtypes.SequenceType(name='person1')
        >>> seq['age'] = dtypes.BaseType(name='age', type='Int32', data=[1,2,3,5,8])
        >>> seq['stuff'] = dtypes.SequenceType(name='stuff')
        >>> seq['stuff']['foo'] = dtypes.BaseType(name='foo', type='Int16',data=[[i*80 + j*16 for j in range(5)] for i in range(5)])
        >>> print list(seq.data)
        [(1, ([0, 16, 32, 48, 64],)), (2, ([80, 96, 112, 128, 144],)), (3, ([160, 176, 192, 208, 224],)), (5, ([240, 256, 272, 288, 304],)), (8, ([320, 336, 352, 368, 384],))]
        >>> testdata = urllib.urlopen("http://dods.coas.oregonstate.edu:8080/dods/dts/NestedSeq.dods").read()
        >>> testdata = testdata[testdata.index("Data:\n")+6:]
        >>> assert testdata == ''.join(build(dataset))
    """
    func = {dtypes.DatasetType  : _dataset,
            dtypes.StructureType: _structure,
            dtypes.SequenceType : _sequence,
            dtypes.BaseType     : _base,
            dtypes.ArrayType    : _array,
            dtypes.GridType     : _grid,
           }[type(dapvar)]

    return func(dapvar, data)


def _dataset(dapvar, data=None):
    for var in dapvar.values():
        for dods_ in build(var):
            yield dods_
                

def _structure(dapvar, data=None):
    if data is None: 
        for var in dapvar.values():
            for dods_ in build(var):
                yield dods_
    
    # Inside a Sequence.
    else:
        # Make data iterable.
        if not isiterable(data): data = [data]
    
        # Propagate data.
        for var,vardata in itertools.izip(dapvar.values(), data):
            # Check for sequences.
            if isinstance(var, dtypes.SequenceType):
                vardata = itertools.izip(*vardata)

            for dods_ in build(var, data=vardata):
                yield dods_


def _sequence(dapvar, data=None):
    if data is None: data = dapvar.data

    for data_ in data:
        yield '\x5a\x00\x00\x00'

        # Make data iterable.
        if not isiterable(data_): data_ = [data_]

        # Propagate data.
        for var,vardata in itertools.izip(dapvar.values(), data_):
            # Check for sequences.
            if isinstance(var, dtypes.SequenceType):
                vardata = itertools.izip(*vardata)

            # Set data on variable and get the response.
            for dods_ in build(var, data=vardata):
                yield dods_

    # End of instance marker.
    yield '\xa5\x00\x00\x00'


def _base(dapvar, data=None):
    if data is None: data = dapvar.data
    return DapPacker(dapvar, data)

_array = _base


def _grid(dapvar, data=None):
    for dods_ in build(dapvar.array, data=data):
        yield dods_
    for map_ in dapvar.maps.values():
        for dods_ in build(map_):
            yield dods_


def _test():
    import doctest
    doctest.testmod()

if __name__ == "__main__":
    _test()

