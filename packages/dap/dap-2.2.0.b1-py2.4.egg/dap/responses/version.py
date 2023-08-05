"""Version response."""

import dap


def build(self, constraints=None):
    headers = [('XDODS-Server', 'dods/%s' % '.'.join([str(i) for i in dap.__dap__])),
               ('Content-type', 'text/plain'),
              ]

    output = ['Core version: dods/%s\n' % '.'.join([str(i) for i in dap.__dap__]),
              'Server version: pydap/%s\n' % '.'.join([str(i) for i in dap.__version__])]

    return headers, output
