"""DAP server.

This module contains a base class for data plugins. This class implements
the basic responses (DAS, DDS, DODS, ASCII, HMTL) and a JSON response 
(http://json.org) for the DAP server.
"""

__author__ = "Roberto De Almeida <rob@pydap.org>"

import os
import sys
import signal
import BaseHTTPServer
import types
import inspect
import pprint
from urllib import splitquery
from cgi import escape as escape_

import dap
from dap import responses, INDENT
from dap.helper import trim, construct_url, linkify
from dap.lib import escape


class BaseHandler(object):
    """Base handler for plugins.

    This class defines the basic functionality required for plugins. New
    data formats can be supported by subclassing ``BaseHandler`` and 
    overwriting the method ``_parseconstraints`` (and possibly ``__init__``)
    to return the desired dataset from a filepath.
    """
    # Basic attributes that every handler instance should have. Specific
    # plugins should overwrite this according to the file being requested.
    filename = 'unknown'
    description = 'no description'
    
    def __init__(self, filepath=None, environ=None):
        self.filepath = filepath
        self.environ = environ

    def _parseconstraints(self, constraints=None):
        """Parses a constraint expression and returns a dataset.
        
        When writing a plugin, redefine this method to parse the constraint
        expression and return the proper dataset build from the classes in
        ``dap.dtypes``.
        """
        raise NotImplementedError("Subclasses must implement _parseconstraints") 
    
    def dds(self, constraints=None):
        """Dataset Descriptor Structure (DDS) response."""
        dataset = self._parseconstraints(constraints)

        # Headers.
        headers = [('Content-description', 'dods_dds'),
                   ('XDODS-Server', 'dods/%s' % '.'.join([str(i) for i in dap.__dap__])),
                   ('Content-type', 'text/plain'),
                  ]

        return headers, responses.dds.build(dataset)

    def das(self, constraints=None):
        """Dataset Attribute Structure (DAS) response."""
        dataset = self._parseconstraints(None)

        # Headers.
        headers = [('Content-description', 'dods_das'),
                   ('XDODS-Server', 'dods/%s' % '.'.join([str(i) for i in dap.__dap__])),
                   ('Content-type', 'text/plain'),
                  ]

        return headers, responses.das.build(dataset)

    def json(self, constraints=None):
        """JavaScript Object Notation (JSON) response."""
        dataset = self._parseconstraints(constraints)

        # Headers.
        headers = [('Content-description', 'dods_json'),
                   ('XDODS-Server', 'dods/%s' % '.'.join([str(i) for i in dap.__dap__])),
                   ('Content-type', 'text/x-json'),
                  ]

        output = responses.json.build(dataset)
        output = pprint.pformat(output)
        output = [output]

        return headers, output

    def dods(self, constraints=None):
        """XDR-encoded binary response."""
        dataset = self._parseconstraints(constraints)

        # Headers.
        headers = [('Content-description', 'dods_data'),
                   ('XDODS-Server', 'dods/%s' % '.'.join([str(i) for i in dap.__dap__])),
                   ('Content-type', 'application/octet-stream'),
                  ]

        def output(dataset):
            for line in responses.dds.build(dataset):
                yield line

            yield 'Data:\n'

            # No linebreak between items here.
            for dods in responses.dods.build(dataset):
                yield dods

        return headers, output(dataset) 

    def ascii(self, constraints=None):
        """ASCII response."""
        dataset = self._parseconstraints(constraints)

        # Headers.
        headers = [('Content-description', 'dods_ascii'),
                   ('XDODS-Server', 'dods/%s' % '.'.join([str(i) for i in dap.__dap__])),
                   ('Content-type', 'text/plain'),
                  ]

        def output(dataset):
            for line in responses.dds.build(dataset):
                yield line

            yield 45 * '-'
            yield '\n'

            for ascii in responses.ascii.build(dataset):
                yield ascii

        return headers, output(dataset)
    asc = ascii

    def html(self, constraints=None):
        """Build a HTML form to retrieve the data."""
        dataset = self._parseconstraints()

        # Headers.
        headers = [('Content-description', 'dods_form'),
                   ('XDODS-Server', 'dods/%s' % '.'.join([str(i) for i in dap.__dap__])),
                   ('Content-type', 'text/html'),
                  ]

        #title = 'DODS Dataset Access Form for %s' % self.filename
        title = 'DODS server: %s' % self.description
        location = construct_url(self.environ)
        if location.endswith('/'): location = location[:-1]

        data = []
        data.append('<?xml version="1.0" encoding="UTF-8"?>\n')
        data.append('<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">\n')
        data.append('<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en" lang="en">\n\n')

        data.append('<head>\n<title>%s</title>\n' % title)
        data.append('<script type="text/javascript" src="http://pydap.org/js/%s/udunits.js"></script>\n' % '.'.join([str(i) for i in dap.__version__]))
        data.append('<script type="text/javascript" src="http://pydap.org/js/%s/strideupdate.js"></script>\n' % '.'.join([str(i) for i in dap.__version__]))
        data.append('</head>\n\n')

        data.append('<body>\n<h1>DODS Dataset Access Form for %s</h1>\n\n' % linkify(location))

        data.extend(responses.html.build(dataset))
        
        data.append('<hr />\n<pre>\n<code>%s</code>\n</pre>\n\n' % ''.join(responses.dds.build(dataset)))
        data.append('<hr />\n<p><em><a href="http://pydap.org">pydap/%s</a></em> &copy; %s</p>\n\n' % ('.'.join([str(i) for i in dap.__version__]), escape_(__author__)))
        data.append('</body>\n</html>')

        return headers, data

    def error(self, info):
        """Error response."""
        headers = [('Content-description', 'dods_error'),
                   ('XDODS-Server', 'dods/%s' % '.'.join([str(i) for i in dap.__dap__])),
                   ('Content-type', 'text/plain'),
                  ]

        data = []
        data.append('Error {\n')
        data.append('%scode = %s;\n' % (INDENT, getattr(info[0], 'code', 0)))
        data.append('%smessage = %s;\n' % (INDENT, escape(getattr(info[1], 'value', str(info[1])))))
        data.append('}')

        return headers, data

    def version(self, constraints=None):
        """Protocol and server version response."""
        headers = [('XDODS-Server', 'dods/%s' % '.'.join([str(i) for i in dap.__dap__])),
                   ('Content-type', 'text/plain'),
                  ]

        data = []
        data.append('Core version: dods/%s\n' % '.'.join([str(i) for i in dap.__dap__]))
        data.append('Server version: pydap/%s\n' % '.'.join([str(i) for i in dap.__version__]))

        return headers, data
    ver = version

    def help(self, constraints=None, message=None):
        """Help response.
        
        Return the supported extensions, found dynamically.
        """
        headers = [('XDODS-Server', 'dods/%s' % '.'.join([str(i) for i in dap.__dap__])),
                   ('Content-type', 'text/html'),
                  ]

        data = []
        if message: data.append(message)

        # Check which extensions the server supports. We check for the
        # 'constraints' argument in methods which don't start with '_'.
        extensions = []
        for attr in dir(self):
            if not attr.startswith('_') and \
            isinstance(getattr(self, attr), types.MethodType):
                args = inspect.getargspec(getattr(self, attr))[0]
                if args == ['self', 'constraints']: extensions.append(attr)

        # Join with commas and finally with 'and'.
        extensions = ['<code>%s</code>' % ext for ext in extensions]
        extensions_ = ', '.join(extensions[:-1])
        extensions = '%s and %s' % (extensions_, extensions[-1])

        data.append("<p>This server supports the %s extensions." % extensions)
        return headers, data


class serve(object):
    """Serve a ``DatasetType`` object.

    This function serves a ``DatasetType`` object on the specified port. It's
    mostly used for simple debugging and for testing the client.
    """
    def __init__(self, dataset, port=8889):
        """Serve a dataset.

        This class forks into background, while serving a given dataset
        on the specified port. Let's build a dataset:

            >>> from dap import dtypes
            >>> dataset = dtypes.DatasetType(name='test')
            >>> dataset['a'] = dtypes.BaseType(name='a', data=42, type='Int32')

        Now we can serve it:
        
            >>> server = serve(dataset, 8887)

        And access it with the client:
        
            >>> from dap.client import open
            >>> dataset2 = open("http://localhost:8887/")
            >>> from dap.responses import dds
            >>> print ''.join(dds.build(dataset2))
            Dataset {
                Int32 a;
            } test;
            <BLANKLINE>

        And finally, close the server:

            >>> server.close()
        """
        class SimpleHandler(BaseHandler):
            """A very simple handler.
            
            This handler calls the magic trim() function to process the
            dataset according to the constraint expression.
            """
            def __init__(self): pass

            def _parseconstraints(self, constraints=None):
                return trim(dataset, constraints)

        class SimpleServer(BaseHTTPServer.BaseHTTPRequestHandler):
            """A very simple server.

            This server passes request for the pages 'dds', 'das', etc. to
            the methods with the same name from the SimpleHandler object.
            """
            def do_GET(self):
                file_, query = splitquery(self.path)
                if file_.startswith('/'): file_ = file_[1:]

                # Remove leading period from requested file.
                entity = file_[1:]

                s = SimpleHandler()
                try:
                    headers, data = getattr(s, entity)(query)
                except:
                    # Capture all errors and format them properly.
                    headers, data = s.error(sys.exc_info()) 

                # Send response, headers.
                self.send_response(200)
                for header in headers:
                    self.send_header(*header)
                self.end_headers()

                # Send data.
                for line in data:
                    self.wfile.write(line)

        # Fork into background, storing the pid.
        try:
            self.pid = os.fork()
            if self.pid == 0:
                # Serve forever.
                TestServer = BaseHTTPServer.HTTPServer(('', port), SimpleServer)
                TestServer.serve_forever()

        except OSError, e:
            print >>sys.stderr, "fork failed: %d (%s)" % (e.errno, e.strerror)

    def __del__(self):
        """Kill the forked process."""
        os.kill(self.pid, signal.SIGKILL)
    close = __del__


def _test():
    import doctest
    doctest.testmod()

if __name__ == "__main__":
    _test()
