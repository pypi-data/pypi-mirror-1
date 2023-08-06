"""Version response."""

from dap.lib import __dap__, __version__


def build(self, constraints=None):
    headers = [('XDODS-Server', 'dods/%s' % '.'.join([str(i) for i in __dap__])),
               ('Content-type', 'text/plain'),
              ]

    output = ['Core version: dods/%s\n' % '.'.join([str(i) for i in __dap__]),
              'Server version: pydap/%s\n' % '.'.join([str(i) for i in __version__])]

    return headers, output
