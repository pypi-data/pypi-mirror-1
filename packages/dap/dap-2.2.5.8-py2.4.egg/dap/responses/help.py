from paste.request import construct_url

from dap.lib import __dap__


def build(self, constraints=None, message=''):

    """Help response."""

    headers = [('XDODS-Server', 'dods/%s' % '.'.join([str(i) for i in __dap__])),
               ('Content-type', 'text/html'),
              ]

    if message:
        output = [message]
    else:
        location = construct_url(self.environ, with_query_string=False)[:-len('.help')]
        output = ["<p>To access this file, use the URL <code>%s</code>.</p>" % location]
                                                                                                                
    return headers, output
