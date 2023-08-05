"""DAP client interface.

The client connects to a dataset served in a given URL and returns a 
representation of the dataset using Python objects. These objects can be
sliced to retrieve the data from the server transparently.
"""

__author__ = "Roberto De Almeida <rob@pydap.org>"

from dap.util import http


def open(url):
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
    pass


def _json(baseurl):
    # Try to read a JSON response from a (pydap?) server.
    jsonurl = '%s.json' % baseurl
    json = http.fetch(jsonurl)

    if json['status'] == 200:
        from dap.parsers.json import JSONParser
        # Build dataset.
        dataset = JSONParser(json['data'], jsonurl)[0]  # return only the first dataset?
        return dataset
