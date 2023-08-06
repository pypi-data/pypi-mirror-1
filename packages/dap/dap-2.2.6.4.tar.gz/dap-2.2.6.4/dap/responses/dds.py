"""
DDS DAP response.

This module implements the DDS DAP response, building it 
dynamically from datasets objects.
"""

__author__ = "Roberto De Almeida <rob@pydap.org>"

from dap.lib import INDENT, __dap__
from dap.dtypes import *  
from dap.dtypes import _basetypes


def build(self, constraints=None):
    dataset = self._parseconstraints(constraints)
    
    headers = [('Content-description', 'dods_dds'),
               ('XDODS-Server', 'dods/%s' % '.'.join([str(i) for i in __dap__])),
               ('Content-type', 'text/plain'),
              ]

    output = _dispatch(dataset)

    return headers, output

    
def _dispatch(dapvar, level=0):
    func = {DatasetType  : _dataset,
            StructureType: _structure,
            SequenceType : _sequence,
            GridType     : _grid,
            ArrayType    : _array,
            BaseType     : _base,
           }[type(dapvar)]

    return func(dapvar, level)
    

def _dataset(dapvar, level=0):
    yield '%sDataset {\n' % (level * INDENT)

    # Get the DDS from stored variables.
    for var in dapvar.walk():
        for line in _dispatch(var, level=level+1):
            yield line
    yield '%s} %s;\n' % (level * INDENT, dapvar.name)


def _structure(dapvar, level=0):
    yield '%sStructure {\n' % (level * INDENT)

    # Get the DDS from stored variables.
    for var in dapvar.walk():
        for line in _dispatch(var, level=level+1):
            yield line
    yield '%s} %s;\n' % (level * INDENT, dapvar.name)


def _sequence(dapvar, level=0):
    yield '%sSequence {\n' % (level * INDENT)

    # Get the DDS from stored variables.
    for var in dapvar.walk():
        for line in _dispatch(var, level=level+1):
            yield line
    yield '%s} %s;\n' % (level * INDENT, dapvar.name)


def _grid(dapvar, level=0):
    yield '%sGrid {\n' % (level * INDENT)

    # Get the DDS from the array...
    yield '%sArray:\n' % ((level+1) * INDENT)
    for line in _dispatch(dapvar.array, level=level+2):
        yield line

    # ...and also from the maps.
    yield '%sMaps:\n' % ((level+1) * INDENT)
    for map_ in dapvar.maps.values():
        for line in _dispatch(map_, level=level+2):
            yield line

    yield '%s} %s;\n' % (level * INDENT, dapvar.name)


def _array(dapvar, level=0):
    # Get the var shape and dimensions, if any.
    if dapvar.dimensions:
        dims = ['%s = %d' % dim for dim in zip(dapvar.dimensions, dapvar.shape)]
    else:
        if len(dapvar.shape) == 1:
            dims = ['%s = %d' % (dapvar.name, dapvar.shape[0])]
        else:
            dims = ['%d' % i for i in dapvar.shape]
    shape = ']['.join(dims)
    shape = '[%s]' % shape 

    yield '%s%s %s%s;\n' % (level * INDENT, dapvar.type, dapvar.name, shape)


def _base(dapvar, level=0):
    yield '%s%s %s;\n' % (level * INDENT, dapvar.type, dapvar.name)


def _test():
    import doctest
    doctest.testmod()

if __name__ == "__main__":
    _test()

