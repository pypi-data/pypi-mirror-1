"""ASCII DAP response.

This module implements the ASCII DAP response, building it 
dynamically from datasets objects.
"""

__author__ = "Roberto De Almeida <rob@pydap.org>"

import itertools

from dap.lib import INDENT, __dap__, encode_atom, isiterable
from dap.dtypes import *


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
    """
    if not t:
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


def build(self, constraints=None):
    dataset = self._parseconstraints('')
    dataset = self._parseconstraints(constraints)

    headers = [('Content-description', 'dods_ascii'),
               ('XDODS-Server', 'dods/%s' % '.'.join([str(i) for i in __dap__])),
               ('Content-type', 'text/plain'),
              ]

    def output(dataset):
        foo, dds = self.dds(constraints)
        for line in dds: yield line
        yield 45 * '-'
        yield '\n'

        for line in _dispatch(dataset): yield line

    return headers, output(dataset)


def _dispatch(dapvar, printname=True):
    func = {DatasetType  : _dataset,
            StructureType: _structure,
            SequenceType : _sequence,
            GridType     : _grid,
            ArrayType    : _array,
            BaseType     : _base,
           }[type(dapvar)]

    return func(dapvar, printname)


def _dataset(dapvar, printname):
    for var in dapvar:
        for line in _dispatch(var, printname):
            yield line
        yield '\n\n'

_structure = _dataset
_grid = _dataset


def _sequence(dapvar, printname):
    yield ', '.join([var.id for var in dapvar.values()])
    yield '\n'
    for struct_ in dapvar:
        out = []
        for var in struct_:
            for line in _dispatch(var, printname=False):
                out.append(line)
        yield ', '.join(out)
        yield '\n'


def _array(dapvar, printname):
    if printname:
        yield dapvar.id
        yield '\n'

    first = True
    data = getattr(dapvar.data, 'flat', dapvar.data)
    for indexes, value in itertools.izip(n_iterate(dapvar.shape), data):
        if first: first = False
        else: yield '\n'

        index = ']['.join([str(idx) for idx in indexes])
        index = '[%s]' % index
        yield '%s %s' % (index, encode_atom(value))


def _base(dapvar, printname):
    if printname:
        yield dapvar.id
        yield '\n'
    yield encode_atom(dapvar.data)


def _test():
    import doctest
    doctest.testmod()

if __name__ == "__main__":
    _test()

