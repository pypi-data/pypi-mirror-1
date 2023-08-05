"""DDS DAP response.

This module implements the DDS DAP response, building it 
dynamically from datasets objects.
"""

__author__ = "Roberto De Almeida <rob@pydap.org>"

from dap import dtypes, INDENT


def build(dapvar, level=0):
    """Build a DDS from a DAP object.

        >>> dataset = dtypes.DatasetType(name='data')
        >>> dataset['catalog_number'] = dtypes.BaseType(name='catalog_number', type='int')
        >>> dataset['casts'] = dtypes.SequenceType(name='casts')
        >>> dataset['casts']['experimenter'] = dtypes.BaseType(name='experimenter',  type='string')
        >>> dataset['casts']['time'] = dtypes.BaseType(name='time', type='int32', attributes={'units': "hour since 0000-01-01 00:00:00", 'time_origin': "1-JAN-0000 00:00:00"})
        >>> dataset['casts']['location'] = dtypes.StructureType(name='location')
        >>> dataset['casts']['location']['latitude'] = dtypes.BaseType(name='latitude', type='Float64', attributes={'long_name': "Latitude", 'units': "degrees_north"})
        >>> dataset['casts']['location']['longitude'] = dtypes.BaseType(name='longitude', type='Float64', attributes={'long_name': "Longitude", 'units': "degrees_east"})
        >>> dataset['casts']['xbt'] = dtypes.SequenceType(name='xbt')
        >>> dataset['casts']['xbt']['depth'] = dtypes.BaseType(name='depth', type='float', attributes={'units': "meters"})
        >>> dataset['casts']['xbt']['temperature'] = dtypes.BaseType(name='temperature', type='float', attributes={'missing_value': -9.99e33, '_fillvalue': -9.99e33, 'history': "From coads_climatology", 'units': "Deg C"})
        >>> print ''.join(build(dataset)).strip()
        Dataset {
            int catalog_number;
            Sequence {
                string experimenter;
                int32 time;
                Structure {
                    Float64 latitude;
                    Float64 longitude;
                } location;
                Sequence {
                    float depth;
                    float temperature;
                } xbt;
            } casts;
        } data;

    """
    func = {dtypes.DatasetType  : _dataset,
            dtypes.StructureType: _structure,
            dtypes.SequenceType : _sequence,
            dtypes.BaseType     : _base,
            dtypes.ArrayType    : _array,
            dtypes.GridType     : _grid,
           }[type(dapvar)]

    return func(dapvar, level)
    

def _dataset(dapvar, level=0):
    yield '%sDataset {\n' % (level * INDENT)

    # Get the DDS from stored variables.
    for var in dapvar.values():
        for dds_ in build(var, level=level+1):
            yield dds_

    yield '%s} %s;\n' % (level * INDENT, dapvar.name)


def _structure(dapvar, level=0):
    yield '%sStructure {\n' % (level * INDENT)

    # Get the DDS from stored variables.
    for var in dapvar.values():
        for dds_ in build(var, level=level+1):
            yield dds_

    yield '%s} %s;\n' % (level * INDENT, dapvar.name)


def _sequence(dapvar, level=0):
    yield '%sSequence {\n' % (level * INDENT)

    # Get the DDS from stored variables.
    for var in dapvar.values():
        for dds_ in build(var, level=level+1):
            yield dds_

    yield '%s} %s;\n' % (level * INDENT, dapvar.name)


def _base(dapvar, level=0):
    yield '%s%s %s;\n' % (level * INDENT, dapvar.type, dapvar.name)


def _array(dapvar, level=0):
    if dapvar.dimensions:
        dims = ['%s = %d' % (i,j) for i,j in zip(dapvar.dimensions, dapvar.shape)]
    else:
        if len(dapvar.shape) == 1:
            dims = ['%s = %d' % (dapvar.name, dapvar.shape[0])]
        else:
            dims = ['%d' % i for i in dapvar.shape]
    dims = ']['.join(dims)
    dims = '[%s]' % dims
    yield '%s%s %s%s;\n' % (level * INDENT, dapvar.type, dapvar.name, dims)


def _grid(dapvar, level=0):
    yield '%sGrid {\n' % (level * INDENT)

    yield '%sArray:\n' % ((level+1) * INDENT)
    for dds_ in build(dapvar.array, level=level+2):
        yield dds_

    yield '%sMaps:\n' % ((level+1) * INDENT)
    for map_ in dapvar.dimensions:
        var = dapvar.maps[map_]
        for dds_ in build(var, level=level+2):
            yield dds_

    yield '%s} %s;\n' % (level * INDENT, dapvar.name)


def _test():
    import doctest
    doctest.testmod()

if __name__ == "__main__":
    _test()

