"""DAP server WSGI application.

This module implements a DAP server over the WSGI specification. For more
information, read http://www.python.org/peps/pep-0333.html.
"""

__author__ = "Roberto De Almeida <rob@pydap.org>"

import sys
import os
import re

from paste.httpexceptions import HTTPNotFound
from paste.request import construct_url
from pkg_resources import iter_entry_points

import dap
from dap.plugins import loadplugins, loadhandler
from dap.server import BaseHandler, SimpleHandler


def make_app(global_conf, root, **kwargs):
    return DapServerApplication(root, **kwargs)


class SimpleApplication(object):
    def __init__(self, dataset):
        self.dataset = dataset

    def __call__(self, environ, start_response):
        self.environ = environ
        self.start = start_response

        return self

    def __iter__(self):
        status = '200 OK'
        try:
            response_headers, output = self.handlerequest()
        except HTTPNotFound:
            status = '404 Not Found'
            self.handler = BaseHandler(environ=self.environ)
            response_headers, output = self.handler.help(message='File not found!')

        self.start(status, response_headers)
        for line in output:
            yield line

    def handlerequest(self):
        # Remove the leading '/'.
        request = self.environ.get('PATH_INFO', '')
        if request.startswith('/'): request = request[1:]

        if not request:
            # Show list of responses.
            message = ['<a href="/%s">%s</a>' % (ep.name, ep.name) for ep in iter_entry_points("dap.response")]
            message = ' | '.join(message)
            response = SimpleHandler(self.dataset, environ=self.environ).help(message=message)
        else:
            entity = request.split('.')[-1]
            self.handler = SimpleHandler(self.dataset, environ=self.environ)
            call = getattr(self.handler, entity)
            response = call(self.environ.get('QUERY_STRING', ''))

        return response
        
    def close(self):
        # Close handler.
        try: self.handler.close()
        except: pass


class DapServerApplication(SimpleApplication):
    def __init__(self, root, name="pyDAP server", verbose=False):
        # Ensure that root ends with /.
        if not root.endswith('/'): root = '%s/' % root
        
        self.root = root
        self.name = name

        # Set verbose option.
        dap.VERBOSE = verbose

        self.plugins = loadplugins()

    def handlerequest(self):
        # Remove the leading '/'.
        request = self.environ.get('PATH_INFO', '')
        if request.startswith('/'): request = request[1:]

        # Special requests.
        if request in ['version', 'help']:
            self.handler = BaseHandler(environ=self.environ)
            call = getattr(self.handler, request)
            return call()
        
        request = os.path.join(self.root, request)

        # Directory listing.
        if os.path.exists(request) and os.path.isdir(request):
            return self.listfiles(request)

        # Strip file suffix.
        entity = request.split('.')[-1]
        file_ = request[:-len(entity)-1]

        if not os.path.exists(file_): raise HTTPNotFound  # 404

        # Call appropriate plugin.
        self.handler = loadhandler(file_, self.environ, self.plugins)
        call = getattr(self.handler, entity)
        response = call(self.environ['QUERY_STRING'])

        return response

    def listfiles(self, dir):
        headers = [('XDODS-Server', 'dods/%s' % '.'.join([str(i) for i in dap.__dap__])),
                   ('Content-type', 'text/html'), ]

        location = construct_url(self.environ, with_query_string=False)
        if location.endswith('/'): location = location[:-1]
        title = 'DODS directory for %s' % location

        data = ["""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en" lang="en">

<head>
<title>%s</title>
</head>

<body>
<h1>DODS directory for %s</h1>
<hr />
<table>\n""" % (title, location)]

        # Check which files are supported by plugins.
        res = [plugin.load().extensions for plugin in iter_entry_points('dap.plugin')]

        dirs, files = [], []
        for item in os.listdir(dir):
            path = os.path.join(dir, item)
            url = os.path.join(location, item)
            if os.path.isdir(path):
                dirs.append(url)
            else:
                # Add only supported files.
                for regexp in res:
                    if re.match(regexp, url):
                        files.append(url)
                        break

        # Add parent dir.
        if dir != self.root:
            parent = location.split('/')[:-1]
            parent = '/'.join(parent)
            data.append('<tr><td colspan="3"><a href="%s">Parent directory</a></td></tr>\n' % parent)

        # Add directories.
        for dir_ in dirs:
            dirname = '%s/' % dir_.split('/')[-1]
            data.append('<tr><td colspan="3"><a href="%s">%s</a></td></tr>\n' % (dir_, dirname))

        # Add files.
        for file_ in files:
            filename = file_.split('/')[-1]
            data.append('''<tr><td>%s</td>
<td><a href="%s.dds">[<acronym title="Dataset Descriptor Structure">DDS</acronym>]</a></td>
<td><a href="%s.das">[<acronym title="Dataset Attribute Structure">DAS</acronym>]</a></td></tr>\n''' % (filename, file_, file_))

        data.append('''</table>
<hr />
<p><em><a href="http://pydap.org">pydap/%s</a></em> &copy; Roberto De Almeida</p>

</body>
</html>''' % '.'.join([str(_) for _ in dap.__version__]))

        return headers, data


if __name__ == "__main__":
    import os
    import optparse

    from paste.httpserver import serve

    parser = optparse.OptionParser()
    parser.add_option('-p', '--port', dest='port',
                      default=8888, type='int',
                      help="port to serve on (default 8888)")
    options, args = parser.parse_args()
                      
    # Get the app root. Defaults to current directory.
    pwd = os.environ['PWD']
    if not len(args) == 1: root = pwd
    else: root = os.path.join(pwd, args[0])

    app = DapServerApplication(root)
    serve(app, port=options.port, host='127.0.0.1')
