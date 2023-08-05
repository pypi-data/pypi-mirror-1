"""DODS DAP response.

This module implements the DODS DAP response, building it
dynamically from datasets objects.
"""

__author__ = "Roberto De Almeida <rob@pydap.org>"

import itertools

from dap import dtypes
from dap.lib import __dap__, isiterable
from dap.xdr import DapPacker


def build(self, constraints=None):
    dataset = self._parseconstraints(constraints)

    headers = [('Content-description', 'dods_data'),
               ('XDODS-Server', 'dods/%s' % '.'.join([str(i) for i in __dap__])),
               ('Content-type', 'application/octet-stream'),
              ]
    
    def output(dataset):
        foo, dds = self.dds(constraints)
        for line in dds: yield line

        yield 'Data:\n'

        for line in _dispatch(dataset): yield line

    return headers, output(dataset)


def _dispatch(dapvar, data=None):
    r"""Build a DODS from a DAP object.
        
        >>> dataset = dtypes.DatasetType(name='temp.dat')
        >>> dataset['Tmp'] = dtypes.ArrayType(name='Tmp', shape=[5], type='Int32', data=range(5))
        >>> for line in _dispatch(dataset):
        ...     print repr(line)
        '\x00\x00\x00\x05\x00\x00\x00\x05'
        '\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x02\x00\x00\x00\x03\x00\x00\x00\x04'
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
    for var in dapvar.walk():
        for line in _dispatch(var):
            yield line

_structure = _dataset
_grid = _dataset
                

def _sequence(dapvar, data=None):
    for struct_ in dapvar:
        yield '\x5a\x00\x00\x00'
        for line in _dispatch(struct_): yield line
    yield '\xa5\x00\x00\x00'


def _base(dapvar, data=None):
    return DapPacker(dapvar)

_array = _base


def _test():
    import doctest
    doctest.testmod()

if __name__ == "__main__":
    _test()

