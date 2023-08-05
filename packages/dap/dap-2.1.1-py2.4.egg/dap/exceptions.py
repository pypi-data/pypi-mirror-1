"""DAP exceptions.

These exceptions are mostly used by the server. When an exception is
captured, a proper error message is displayed (according to the DAP
2.0 spec), with information about the exception and the error code 
associated with it.
"""

__author__ = "Roberto De Almeida <rob@pydap.org>"


class DapError(Exception):
    """Base DAP exception."""
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)

class OpenFileError(DapError):
    """Exception raised when unable to open a file."""
    code = 1

class ConstraintExpressionError(DapError):
    """Exception raised when an invalid constraint expression is given."""
    code = 2

class ExtensionNotSupportedError(DapError):
    """Exception raised when trying to open a file not supported by any plugins."""
    code = 3

class PluginError(DapError):
    """Generic error with a plugin."""
    code = 4
