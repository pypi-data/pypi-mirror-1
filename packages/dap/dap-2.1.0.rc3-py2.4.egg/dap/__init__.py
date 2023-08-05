__author__ = 'Roberto De Almeida <rob@pydap.org>'
__version__ = (2,1,0,'rc3')  # module version
__dap__ = (2,0)        # protocol version

# Indentation for the DAS/DDS.
INDENT = ' ' * 4

# User agent for the client.
USER_AGENT = 'pydap/%s' % '.'.join([str(_) for _ in __version__])

# Timeout for connections when retrieving data (seconds).
TIMEOUT = 120

# Preferred numerical module. If you have more than one installed, you can
# change the order of the imports here to specify the one you prefer.
try:
    # Numeric Python
    from Numeric import array
except ImportError:
    try:
        # Scipy Core
        from scipy import array
    except ImportError:
        # Numarray
        from numarray import array
