"""JSON response.

This module implements a JSON response, describing the dataset structure
and attributes. The response is valid Python *and* Javascript code, and can 
be easily parsed by XML HTTP requests.
"""

__author__ = "Roberto De Almeida <rob@pydap.org>"

from dap import dtypes


def build(dataset):
    """Build a JSON response from a DAP object.

        >>> dataset = dtypes.DatasetType(name='data', attributes={'name': "Test Dataset"})
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
        >>> import pprint
        >>> pprint.pprint(build(dataset))
        {'data': {'attributes': {'name': 'Test Dataset'},
                  'casts': {'attributes': {},
                            'experimenter': {'attributes': {},
                                             'pydap_type': 'BaseType',
                                             'type': 'string'},
                            'location': {'attributes': {},
                                         'latitude': {'attributes': {'long_name': 'Latitude',
                                                                     'units': 'degrees_north'},
                                                      'pydap_type': 'BaseType',
                                                      'type': 'Float64'},
                                         'longitude': {'attributes': {'long_name': 'Longitude',
                                                                      'units': 'degrees_east'},
                                                       'pydap_type': 'BaseType',
                                                       'type': 'Float64'},
                                         'pydap_type': 'StructureType'},
                            'pydap_type': 'SequenceType',
                            'time': {'attributes': {'time_origin': '1-JAN-0000 00:00:00',
                                                    'units': 'hour since 0000-01-01 00:00:00'},
                                     'pydap_type': 'BaseType',
                                     'type': 'int32'},
                            'xbt': {'attributes': {},
                                    'depth': {'attributes': {'units': 'meters'},
                                              'pydap_type': 'BaseType',
                                              'type': 'float'},
                                    'pydap_type': 'SequenceType',
                                    'temperature': {'attributes': {'_fillvalue': -9.9899999999999995e+33,
                                                                   'history': 'From coads_climatology',
                                                                   'missing_value': -9.9899999999999995e+33,
                                                                   'units': 'Deg C'},
                                                    'pydap_type': 'BaseType',
                                                    'type': 'float'}}},
                  'catalog_number': {'attributes': {},
                                     'pydap_type': 'BaseType',
                                     'type': 'int'},
                  'pydap_type': 'DatasetType'}}

        >>> dataset = dtypes.DatasetType(name='foo')
        >>> dataset['grid'] = dtypes.GridType(name='grid', dimensions=['x', 'y'], shape=[2,3], type='Int32')
        >>> dataset['grid'].maps['x'] = dtypes.ArrayType(name='x', shape=[2], type='Int32')
        >>> dataset['grid'].maps['y'] = dtypes.ArrayType(name='y', shape=[3], type='Int32')
        >>> pprint.pprint(build(dataset))
        {'foo': {'attributes': {},
                 'grid': {'attributes': {},
                          'dimensions': ['x', 'y'],
                          'maps': {'x': {'attributes': {},
                                         'pydap_type': 'ArrayType',
                                         'shape': [2],
                                         'type': 'Int32'},
                                   'y': {'attributes': {},
                                         'pydap_type': 'ArrayType',
                                         'shape': [3],
                                         'type': 'Int32'}},
                          'pydap_type': 'GridType',
                          'shape': [2, 3],
                          'type': 'Int32'},
                 'pydap_type': 'DatasetType'}}
    """
    out = {}
    out[dataset.name] = _build(dataset)
    return out


def _build(dapvar):
    out = {}
    
    out['pydap_type'] = {dtypes.BaseType     : 'BaseType',
                         dtypes.ArrayType    : 'ArrayType', 
                         dtypes.GridType     : 'GridType',
                         dtypes.SequenceType : 'SequenceType',
                         dtypes.StructureType: 'StructureType',
                         dtypes.DatasetType  : 'DatasetType',
                        }[type(dapvar)]

    # Add basic attributes.
    for attr in ['type', 'shape', 'dimensions', 'attributes']:
        value = getattr(dapvar, attr, None)
        if value is not None:
            if isinstance(value, tuple): value = list(value)
            out[attr] = value
    
    if isinstance(dapvar, dtypes.StructureType):
        for var in dapvar.values():
            out[var.name] = _build(var)
    elif isinstance(dapvar, dtypes.GridType):
        out['maps'] = {}
        for map_ in dapvar.maps.values():
            out['maps'][map_.name] = _build(map_)

    return out
    

def _test():
    import doctest
    doctest.testmod()

if __name__ == "__main__":
    _test()
