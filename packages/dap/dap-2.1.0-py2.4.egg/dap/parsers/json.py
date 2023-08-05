"""JSON parser.

JSON (JavaScript Object Notation) is a subset of the Javascript syntax used
to transmit data à la XML. The biggest advantage of JSON for us is that 
it's also valid *Python* code, so we can easily share data using ``eval()``
and ``pprint()``.
"""

__author__ = "Roberto De Almeida <rob@pydap.org>"

from dap import dtypes, proxy
from dap.util.safeeval import expr_eval


def JSONParser(json, url):
    """A parser for a JSON response describing a dataset.
    
    A simple example. First let's create a simple dataset:

        >>> from dap.responses import json, das, dds
        >>> dataset = dtypes.DatasetType(name='test', attributes={'author': 'Roberto De Almeida'})
        >>> dataset['a'] = dtypes.BaseType(name='a', data=1, type='Int32')

    Here's the JSON response:

        >>> import pprint
        >>> json = pprint.pformat(json.build(dataset))
        >>> print json
        {'test': {'a': {'pydap_type': 'BaseType', 'type': 'Int32', 'attributes': {}},
                  'attributes': {'author': 'Roberto De Almeida'},
                  'pydap_type': 'DatasetType'}}

    Nice. Notice that this is valid Python code, so it will be easy to
    parse it and generate a dataset.

        >>> dataset = JSONParser(json, '')[0]
        >>> print ''.join(das.build(dataset))
        Attributes {
            String author "Roberto De Almeida";
            a {
            }
        }
        <BLANKLINE>

        >>> print ''.join(dds.build(dataset))
        Dataset {
            Int32 a;
        } test;
        <BLANKLINE>
    """
    datasets = expr_eval(json)

    out = []
    for name, dataset in datasets.items():
        out.append(_build(name, dataset, url))

    return out


def _build(name, d, url):
    dtype = getattr(dtypes, d['pydap_type'])
    var = dtype(name=name)

    for k, v in d.items():
        if isinstance(v, dict) and v.get('pydap_type', None):
            var[k] = _build(k, v, url)
        elif k == 'maps':
            for map_ in v:
                var.maps[map_] = _build(map_, v[map_], url)
        elif k != 'pydap_type':
            setattr(var, k, v)

    # Set data proxy. Only for some dtypes?
    location = url[:-5]  # strip .json from URL.
    var.data = proxy.Proxy(location, var)

    return var


def _test():
    import doctest
    doctest.testmod()

if __name__ == "__main__":
    _test()
