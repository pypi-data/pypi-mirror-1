__author__ = "Roberto De Almeida <rob@pydap.org>"

import dap

import httplib2


def open(url, cache=None, username=None, password=None, verbose=False):
    """Connect to a remote dataset.

    This function opens a dataset stored in a DAP server:

        >>> dataset = open(url, cache=None, username=None, password=None, verbose=False):

    You can specify a cache location (a directory), so that repeated
    accesses to the same URL avoid the network.
    
    The username and password may be necessary if the DAP server requires
    authentication. The 'verbose' option will make pydap print all the 
    URLs that are acessed.
    """
    # Set variables on module namespace.
    dap.VERBOSE = verbose
    dap.CACHE = cache

    if url.startswith('http'):
        for response in [_ddx, _ddsdas]:
            dataset = response(url, username, password)
            if dataset: return dataset
        else:
            raise Exception, "Unable to open dataset."
    else:
        from dap.plugins import loadhandler
        # Open a local file. This is a clever hack. :)
        handler = loadhandler(url)
        dataset = handler._parseconstraints()

    return dataset


def _ddsdas(baseurl, username, password):
    h = httplib2.Http(dap.CACHE)
    if username and password: h.add_credentials(username, password)
    
    ddsurl, dasurl = '%s.dds' % baseurl, '%s.das' % baseurl

    # Get metadata.
    if dap.VERBOSE: print ddsurl
    respdds, dds = h.request(ddsurl, "GET")
    if dap.VERBOSE: print dasurl
    respdas, das = h.request(dasurl, "GET")

    if respdds['status'] == '200' and respdas['status'] == '200':
        from dap.parsers.dds import DDSParser
        from dap.parsers.das import DASParser

        # Build dataset.
        dataset = DDSParser(dds, ddsurl).parse()

        # Add attributes.
        dataset = DASParser(das, dasurl, dataset).parse()
        return dataset


def _ddx(baseurl, username, password):
    pass
