"""DAP WSGI application and support functions.

This module implements a DAP server over the WSGI specification. For more
information, read http://www.python.org/peps/pep-0333.html.
"""

__author__ = "Roberto De Almeida <rob@pydap.org>"

import sys
import os
import re
import logging
from cgi import FieldStorage, escape

import dap
from dap.plugins import loadplugins, loadhandler
from dap.server import BaseHandler
from dap.helper import construct_url, linkify


def make_app(global_conf, root, **kwargs):
    return DapServerApplication(root, **kwargs)


class DapServerApplication(object):
    def __init__(self, root, name="pyDAP server"):
        self.root = root
        self.name = name

        self.plugins = loadplugins()

    def __call__(self, environ, start_response):
        self.environ = environ
        self.start = start_response

        # Create logger if there's none.
        self.environ.setdefault('logger', logging)

        self.handler = BaseHandler()
        return self

    def handlerequest(self):
        # Check for POST from form.
        if self.environ['REQUEST_METHOD'] == 'POST':
            form = FieldStorage(fp=self.environ['wsgi.input'],
                                environ=self.environ,
                                keep_blank_values=1)

            # Rewrite form.
            projection = []
            selection = []
            for k in form.keys():
                # Selection.
                if k.startswith('var1') and form.getvalue(k) != '--':
                    name = k[5:]
                    sel = '%s%s%s' % (form.getvalue(k), form.getvalue('op_%s' % name), form.getvalue('var2_%s' % name))
                    selection.append(sel)
                # Projection.
                if form.getvalue(k) == 'on':
                    var = []
                    var.append(k)
                    # This assume ordered dimensions in form.
                    for d in form.keys():
                        if d.startswith('%s_' % k):
                            var.append('[%s]' % form.getvalue(d))

                    var = ''.join(var)
                    if not var in projection:
                        projection.append(var)

            projection = ','.join(projection)
            selection = '&'.join(selection)
            if selection:
                query = '%s&%s' % (projection, selection)
            else:
                query = projection

            # Empty queries SHOULD NOT return everything, because this
            # means the user didn't select any variables.
            if not query:
                headers = [('Content-type', 'text/html')]
                data = ['<p>You did not select any variables. <a href="%s">Return to the form?</a></p>' % self.environ['HTTP_REFERER']]
            else:
                # Replace html extension for ascii.
                redirect = '%s.ascii' % self.environ['HTTP_REFERER'][:-5]

                # Build new URL & update status.
                redirect = '%s?%s' % (redirect, query)
                self.status = '303 Sea Otter'

                headers = [('Location', redirect)]
                data = ['<p>This resource is located <a href="%s">here</a></p>.' % redirect]

            return headers, data
            
        # Remove the leading '/'.
        request = self.environ['PATH_INFO']
        if request.startswith('/'): request = request[1:]
        self.environ['logger'].info('Request: %s' % request)

        # Special requests.
        if request in ['version', 'help']:
            call = getattr(self.handler, request)
            return call()
        
        request = os.path.join(self.root, request)

        if os.path.exists(request) and os.path.isdir(request):
            return self.listfiles(request)
        else:
            if os.path.exists(request):
                file_ = request
                entity = 'help'
            else:
                # Strip file suffix.
                entity = request.split('.')[-1]
                file_ = request[:-len(entity)-1]

                if not os.path.exists(file_):
                    self.status = '404 Not Found'
                    message = 'File not found: %s' % request
                    self.environ['logger'].error(message)
                    return self.handler.help(message=message)

        self.handler = loadhandler(file_, self.environ, self.plugins)
        try:
            # Call the corresponding function from the handler.
            call = getattr(self.handler, entity)
            response = call(self.environ['QUERY_STRING'])
        except:
            self.status = '500 Internal Error'
            response = self.handler.error(sys.exc_info())
            message = ''.join(response[1])
            self.environ['logger'].error('Captured server error: %s' % message)
        return response
            
    def listfiles(self, dir):
        headers = [('XDODS-Server', 'dods/%s' % '.'.join([str(i) for i in dap.__dap__])),
                   ('Content-type', 'text/html'),
                  ]

        location = construct_url(self.environ, with_query_string=False)
        if location.endswith('/'): location = location[:-1]
        title = 'DODS directory for %s' % location

        data = []
        data.append('<?xml version="1.0" encoding="UTF-8"?>\n')
        data.append('<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">\n')
        data.append('<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en" lang="en">\n\n')
                                        
        data.append('<head>\n<title>%s</title>\n</head>\n\n' % title)
        data.append('<body>\n<h1>DODS directory for %s</h1>\n\n' % linkify(location))
        data.append('<hr />\n<table>\n')

        dirs = []
        files = []
        for i in os.listdir(dir):
            path = os.path.join(dir, i)
            url = os.path.join(location, i)
            if os.path.isdir(path):
                dirs.append(url)
            else:
                files.append(url)

        # Add parent dir?
        if not self.environ.get('PATH_INFO', '') in ['/', '']:
            parent = location.split('/')[:-1]
            parent = '/'.join(parent)
            data.append('<tr><td><a href="%s">Parent directory</a></td><td></td><td></td></tr>\n' % parent)

        # Add directories.
        for dir_ in dirs:
            dirname = '%s/' % dir_.split('/')[-1]
            data.append('<tr><td><a href="%s">%s</a></td><td></td><td></td></tr>\n' % (dir_, dirname))
        # Add files that are handled by the plugins.
        for file_ in files:
            for ext in [plugin.extensions for plugin in self.plugins]:
                p = re.compile(ext)
                m = p.match(file_)
                if m:
                    filename = file_.split('/')[-1]
                    data.append('<tr><td><a href="%s.html">%s</a></td>\n' % (file_, filename))
                    data.append('<td><a href="%s.dds">[<acronym title="Dataset Descriptor Structure">DDS</acronym>]</a></td>\n' % file_)
                    data.append('<td><a href="%s.das">[<acronym title="Dataset Attribute Structure">DAS</acronym>]</a></td></tr>\n' % file_)

        data.append('</table>\n\n')
        data.append('<hr />\n<p><em><a href="http://pydap.org">pydap/%s</a></em> &copy; %s</p>\n\n' % ('.'.join([str(i) for i in dap.__version__]), escape(__author__)))
        data.append('</body>\n</html>')

        return headers, data

    def __iter__(self):
        self.status = '200 OK'
        response_headers, output = self.handlerequest()

        self.start(self.status, response_headers)
        for line in output:
            yield line

    def close(self):
        # Close handler.
        if hasattr(self.handler, 'close'):
            self.handler.close()


def _test():
    import doctest
    doctest.testmod()

if __name__ == "__main__":
    _test()
