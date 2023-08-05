"""A Python implementation of the Data Access Protocol (DAP).

PyDAP is a Python module implementing the Data Access Protocol (DAP)
written from scratch. The module implements a DAP client, allowing
transparent and efficient access to dataset stored in DAP server, and
also implements a DAP server able to serve data from a variety of
formats.

For more information about the protocol, please check http://opendap.org.
"""

__author__ = 'Roberto De Almeida <rob@pydap.org>'
__version__ = (2,2,0,'b2')  # module version
__dap__ = (2,0)             # protocol version


# Indentation for the DAS/DDS.
INDENT = ' ' * 4

# User agent for the client.
USER_AGENT = 'pydap/%s' % '.'.join([str(_) for _ in __version__])

# For debugging connections.
VERBOSE = False

# Cache for the client.
CACHE = None

# This is here because I was bored.
FORTY_TWO = 42
