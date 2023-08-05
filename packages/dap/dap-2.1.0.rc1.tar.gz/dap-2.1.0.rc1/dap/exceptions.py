"""DAP exceptions.

These exceptions are mostly used by the server. When an exception is
captured, a proper error message is displayed (according to the DAP
2.0 spec), with information about the exception and the error code 
associated with it.
"""

__author__ = "Roberto De Almeida <rob@pydap.org>"


class DapError(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)

class OpenFileError(DapError):
    code = 1

class ConstraintExpressionError(DapError):
    code = 2

class ExtensionNotSupportedError(DapError):
    code = 3
