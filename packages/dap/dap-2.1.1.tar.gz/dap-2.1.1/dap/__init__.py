"""A Python implementation of the Data Access Protocol (DAP).

PyDAP is a Python module implementing the Data Access Protocol (DAP)
written from scratch. The module implements a DAP client, allowing
transparent and efficient access to dataset stored in DAP server, and
also implements a DAP server able to serve data from a variety of
formats.

For more information about the protocol, please check http://opendap.org.
"""

__author__ = 'Roberto De Almeida <rob@pydap.org>'
__version__ = (2,1,1)  # module version
__dap__ = (2,0)        # protocol version

# Indentation for the DAS/DDS.
INDENT = ' ' * 4

# User agent for the client.
USER_AGENT = 'pydap/%s' % '.'.join([str(_) for _ in __version__])

# Timeout for connections when retrieving data (seconds).
TIMEOUT = 120

# Preferred numerical module. If you have more than one installed, you can
# change the order of the imports here to specify the one you prefer.
arrays = ['Numeric', 'scipy', 'numarray']
for module in arrays:
    try:
        module = __import__(module, globals(), locals(), [])
        array = module.array
        break
    except ImportError:
        pass
else:
    class SimpleArray(list):
        """Stub multidimensional array.

        This is a list-like object used when no implementation of multi-dimensional
        arrays (eg, Numeric or numarray) is found.
        """
        pass
    array = SimpleArray
