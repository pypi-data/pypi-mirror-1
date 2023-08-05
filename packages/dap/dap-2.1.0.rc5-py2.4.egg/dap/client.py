r"""DAP client interface.

The client connects to a dataset served in a given URL and returns a 
representation of the dataset using Python objects. These objects can be
sliced to retrieve the data from the server transparently.

Connecting to a dataset in a DAP server:

    >>> from dap.client import open
    >>> dataset = open("http://server.pydap.org/test/sst.mean.nc")

Checking the variables in the dataset:

    >>> print dataset.keys()
    ['sst', 'time', 'lat', 'lon']

Introspecting a variable:

    >>> sst = dataset['sst']
    >>> print sst.shape
    (173, 90, 180)
    >>> print sst.dimensions
    ['time', 'lat', 'lon']
    >>> import pprint
    >>> pprint.pprint(sst.attributes)
    {'actual_range': [-2.7999999999999998, 36],
     'add_offset': [0],
     'dataset': ['"NMC Real-time Marine\nC"'],
     'level_desc': ['"Surface\n0"'],
     'long_name': ['Sea Surface Temperature Monthly Mean at Surface'],
     'missing_value': [-9.9692099999999994e+36],
     'parent_stat': ['"Individual Obs\nI"'],
     'precision': [2],
     'scale_factor': [1],
     'statistic': ['"Mean\nM"'],
     'units': ['degC'],
     'valid_range': [-5, 40],
     'var_desc': ['"Sea Surface Temperature\nS"']}

Data is only retrieved when the variable is sliced:

    >>> print sst[0,45,90]
    [ [  [ 30.64999962]]]
"""

__author__ = "Roberto De Almeida <rob@pydap.org>"

from dap.util import http


def open(url):
    """Open a dataset or a local file.

    This function is used to open a DAP served dataset, given by an URL:

        >>> dataset = open("http://server.pydap.org/test/sst.mean.nc")

    It can also be used to open local files, provided the necessary
    plugins are installed:

        >>> dataset = open("/path/to/file")

    The advantage is that the same interface to the data can be used both
    for local and remotely stored files.
    """
    if url.startswith('http'):
        for response in [_ddx, _ddsdas, _json]:
            dataset = response(url)
            if dataset: return dataset
        else:
            raise Exception, "Unable to open dataset."
    else:
        from dap.plugins import loadhandler
        # Open a local file. This is a clever hack. :)
        handler = loadhandler(url)
        dataset = handler._parseconstraints()

    return dataset


def _ddsdas(baseurl):
    """Build a dataset from the DAS/DDS response.

    This function builds a dataset representation from the DAS (Dataset
    Attribute Structure) and the DDS (Dataset Descriptor Structure).
    This is the usual way to represent a dataset according to the DAP.
    """
    ddsurl, dasurl = '%s.dds' % baseurl, '%s.das' % baseurl
    dds = http.fetch(ddsurl)
    das = http.fetch(dasurl)

    if dds['status'] == 200 and \
       das['status'] == 200:
        from dap.parsers.dds import DDSParser
        from dap.parsers.das import DASParser
        # Build dataset.
        dataset = DDSParser(dds['data'], ddsurl).parse()

        # Add attributes.
        dataset = DASParser(das['data'], dasurl, dataset).parse()
        return dataset


def _ddx(baseurl):
    """Build a dataset from the DDX response.

    The DDX is a new response designed to replace the DAS/DDS. The DDX
    fully represents the dataset's attributes and structure using a XML
    representation.

    Currently not supported, because the final specifications haven't
    been released.
    """
    pass


def _json(baseurl):
    """Build a dataset from a JSON response.

    The JSON response is a description of the dataset using a simple 
    notation designed to be easily parsed by Javascript (and, incidently,
    by Python). The PyDAP server has the JSON response to simplify the
    development of an AJAX interface to the data.

    This is currently only supported by PyDAP 2.1, and the syntax will
    probably change in the future.
    """
    # Try to read a JSON response from a (pydap?) server.
    jsonurl = '%s.json' % baseurl
    json = http.fetch(jsonurl)

    if json['status'] == 200:
        from dap.parsers.json import JSONParser
        # Build dataset.
        dataset = JSONParser(json['data'], jsonurl)[0]  # return only the first dataset?
        return dataset


def _test():
    import doctest
    doctest.testmod()

if __name__ == "__main__":
    _test()
