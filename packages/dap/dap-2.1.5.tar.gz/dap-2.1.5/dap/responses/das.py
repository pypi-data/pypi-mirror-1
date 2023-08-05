"""DAS DAP response.

This module implements the DAS DAP response, building it
dynamically from datasets objects.
"""

__author__ = "Roberto De Almeida <rob@pydap.org>"

from dap import dtypes, INDENT
from dap.lib import encode_atom


# Type conversion between Python and DODS, for the DAS.
typeconvert = {basestring: 'String',
               str       : 'String',
               float     : 'Float32',
               long      : 'Float64',
               int       : 'Int32',
              }


def _recursive_build(attr, values, level=0):
    """Recursive function to build the DAS.
    
    This function checks for attribute nodes that do not belong to any
    variable, and append them as metadata.
    """        
    # Check for metadata.
    if isinstance(values, dict):
        yield '%s%s {\n' % ((level+1) * INDENT, attr)
        for k,v in values.items():
            for item in _recursive_build(k, v, level+1):
                yield item
        yield '%s}\n' % ((level+1) * INDENT)
    else:
        # Convert values to list.
        if hasattr(values, 'tolist'): values = values.tolist()
        elif not isinstance(values, list): values = [values]

        # Get value type and encode properly.
        attrtype = typeconvert[type(values[0])]
        values = [encode_atom(v) for v in values]
        values = ', '.join(values)

        yield '%s%s %s %s;\n' % ((level+1) * INDENT, attrtype, attr, values)


def build(dapvar, level=0):
    """Build a DAS from a DAP object.

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
        Attributes {
            catalog_number {
            }
            casts {
                experimenter {
                }
                time {
                    String units "hour since 0000-01-01 00:00:00";
                    String time_origin "1-JAN-0000 00:00:00";
                }
                location {
                    latitude {
                        String units "degrees_north";
                        String long_name "Latitude";
                    }
                    longitude {
                        String units "degrees_east";
                        String long_name "Longitude";
                    }
                }
                xbt {
                    depth {
                        String units "meters";
                    }
                    temperature {
                        String units "Deg C";
                        Float32 _fillvalue -9.99e+33;
                        Float32 missing_value -9.99e+33;
                        String history "From coads_climatology";
                    }
                }
            }
        }
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
    yield '%sAttributes {\n' % (level * INDENT)

    # Global attributes and metadata.
    if dapvar.attributes:
        for attr,values in dapvar.attributes.items():
            for item in _recursive_build(attr, values, level):
                yield item

    # Get the DAS from stored variables.
    for var in dapvar.values():
        for das_ in build(var, level=level+1):
            yield das_

    yield '%s}\n' % (level * INDENT)


def _structure(dapvar, level=0):
    yield '%s%s {\n' % (level * INDENT, dapvar.name)

    # Global attributes and metadata.
    if dapvar.attributes:
        for attr,values in dapvar.attributes.items():
            for item in _recursive_build(attr, values, level):
                yield item

    # Get the DAS from stored variables.
    for var in dapvar.values():
        for das_ in build(var, level=level+1):
            yield das_

    yield '%s}\n' % (level * INDENT)

_sequence = _structure


def _base(dapvar, level=0):
    yield '%s%s {\n' % (level * INDENT, dapvar.name)

    # Global attributes and metadata.
    if dapvar.attributes:
        for attr,values in dapvar.attributes.items():
            for item in _recursive_build(attr, values, level):
                yield item

    yield '%s}\n' % (level * INDENT)

_array = _base
_grid = _base


def _test():
    import doctest
    doctest.testmod()

if __name__ == "__main__":
    _test()

