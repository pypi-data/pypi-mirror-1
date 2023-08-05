from pkg_resources import iter_entry_points

from dap.helper import constrain
from dap.lib import escape, INDENT, __dap__


class BaseHandler(object):

    description = 'No description available'

    def __init__(self, filepath=None, environ=None):
        self.filepath = filepath
        self.environ = environ or {}

    def _parseconstraints(self, constraints=None):
        raise NotImplementedError("Subclasses must implement _parseconstraints")

    def error(self, info):
        """Error response."""

        headers = [('Content-description', 'dods_error'),
                   ('XDODS-Server', 'dods/%s' % '.'.join([str(i) for i in __dap__])),
                   ('Content-type', 'text/plain'),
                  ]

        output = ['Error {\n',
                  INDENT, 'code = %s;\n' % getattr(info[0], 'code', 42),
                  INDENT, 'message = %s;\n' % escape(getattr(info[1], 'value', str(info[1]))),
                  '}'
                 ]

        return headers, output


# Load responses from entry points.
for ep in iter_entry_points("dap.response"):
    setattr(BaseHandler, ep.name, ep.load().build)


class SimpleHandler(BaseHandler):

    def __init__(self, dataset, environ=None):
        self.dataset = dataset
        self.environ = environ or {}

    def _parseconstraints(self, constraints=None):
        return constrain(self.dataset, constraints)

