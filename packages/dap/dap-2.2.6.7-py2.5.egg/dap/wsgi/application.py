"""DAP server WSGI application.

This module implements a DAP server over the WSGI specification. For more
information, read http://www.python.org/peps/pep-0333.html.
"""

__author__ = "Roberto De Almeida <rob@pydap.org>"

import sys
import os
import re
import urllib
from urlparse import urljoin

from paste.httpexceptions import HTTPException, HTTPNotFound
from paste.request import construct_url
from paste.deploy.converters import asbool
from paste.wsgilib import intercept_output
from pkg_resources import iter_entry_points
from Cheetah.Template import Template

import dap.lib
from dap.plugins.lib import loadplugins, loadhandler
from dap.server import BaseHandler, SimpleHandler


index_tmpl = """<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en" lang="en">
<head><title>$title</title></head>
<body>
<h1>DODS directory for $location</h1>
<hr />
<table>
#if $parent
    <tr><td colspan="3"><a href="$parent">Parent directory</a></td></tr>
#end if
#for $dir in $dirs:
    #set $dirname = '%s/' % $dir.split('/')[-1]
    <tr><td colspan="3"><a href="$dir">$dirname</a></td></tr>
#end for
#for $file in $files:
    #set $filename = $file.split('/')[-1]
    <tr><td>$filename</td><td><a href="${file}.dds">[<acronym title="Dataset Descriptor Structure">DDS</acronym>]</a></td><td><a href="${file}.das">[<acronym title="Dataset Attribute Structure">DAS</acronym>]</a></td></tr>
#end for
</table>
<hr />
<p><em><a href="http://pydap.org">pydap/$version</a></em> &copy; Roberto De Almeida</p>
</body>
</html> """


def make_app(global_conf, root, **kwargs):
    return DapServerApplication(root, **kwargs)


class SimpleApplication(object):
    def __init__(self, dataset):
        self.dataset = dataset

    def __call__(self, environ, start_response):
        status = '200 OK'
        try:
            headers, output = self.handlerequest(environ)
        except HTTPException, exc:
            # Raise these exceptions so they get 
            # captured by the middleware.
            status, headers, output = intercept_output(environ, exc)
        except:
            status = '500 Internal Error'
            self.handler = BaseHandler(environ=environ)
            headers, output = self.handler.error(sys.exc_info())
            if environ.get('x-wsgiorg.throw_errors'): raise

        start_response(status, headers)
        for line in output:
            yield line

        try:
            self.handler.close()
        except:
            pass

    def handlerequest(self, environ):
        # Remove the leading '/'.
        request = environ.get('PATH_INFO', '').lstrip('/')
        request = urllib.unquote(request)

        if not request:
            # Show list of responses.
            message = ['<a href="/.%s">%s</a>' % (ep.name, ep.name) for ep in iter_entry_points("dap.response")]
            message = ' | '.join(message)
            self.handler = BaseHandler(environ=environ)
            response = self.handler.help(message=message)
        else:
            entity = request.split('.')[-1]
            self.handler = SimpleHandler(self.dataset, environ=environ)
            call = getattr(self.handler, entity)
            response = call(environ.get('QUERY_STRING', ''))

        return response
        

class DapServerApplication(SimpleApplication):
    def __init__(self, root, name="pyDAP server", template=None, verbose=False, **kwargs):
        # Ensure that root ends with /.
        if not root.endswith('/'): root = '%s/' % root
        
        self.root = root
        self.name = name
        self.template = template

        # Set verbose option.
        dap.lib.VERBOSE = asbool(verbose)
        
        # Set additional keywords and ``throw_errors`` key.
        # http://wsgi.org/wsgi/Specifications/throw_errors
        if kwargs.get('x-wsgiorg.throw_errors'):
            kwargs['x-wsgiorg.throw_errors'] = asbool(kwargs['x-wsgiorg.throw_errors'])
        self.to_environ = kwargs

        # And load plugins for data handling.
        self.plugins = loadplugins(throw_errors=kwargs.get('x-wsgiorg.throw_errors', False))

    def handlerequest(self, environ):
        # Update environ with user-defined keys.
        environ.update(self.to_environ)

        # Remove the leading '/'.
        request = environ.get('PATH_INFO', '').lstrip('/')
        request = urllib.unquote(request)

        # Special requests.
        if request in ['version', 'help']:
            self.handler = BaseHandler(environ=environ)
            call = getattr(self.handler, request)
            return call()
        
        request = os.path.join(self.root, request)

        # Directory listing.
        if os.path.exists(request) and os.path.isdir(request):
            return self.listfiles(request, environ)

        # Strip file suffix.
        entity = request.split('.')[-1]
        file_ = request[:-len(entity)-1]

        if not os.path.exists(file_): raise HTTPNotFound  # 404

        # Call appropriate plugin.
        self.handler = loadhandler(file_, environ, self.plugins)
        call = getattr(self.handler, entity)
        response = call(environ.get('QUERY_STRING'))

        return response

    def listfiles(self, dir, environ):
        headers = [('XDODS-Server', 'dods/%s' % '.'.join([str(i) for i in dap.lib.__dap__])),
                   ('Content-Type', 'text/html'),
                   ('Content-Encoding', 'utf-8'), ]

        location = construct_url(environ, with_query_string=False)
        title = 'DODS directory for %s' % location.rstrip('/')

        # Check which files are supported by plugins.
        res = [plugin.extensions for plugin in self.plugins]
        dirs, files = [], []

        # Sort files.
        file_listing = os.listdir(dir)
        file_listing.sort()
        
        for item in file_listing:
            path = os.path.join(dir, item)
            url = urljoin(location, item)
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
            parent = '..'
        else:
            parent = None

        namespace = {'title': title,
                     'location': location,
                     'parent': parent,
                     'dirs': dirs,
                     'files': files,
                     'version': '.'.join([str(_) for _ in dap.lib.__version__])
                    }

        if self.template:
            index = os.path.join(self.template, 'index.tmpl')
            t = Template(file=index, searchList=[namespace], filter='EncodeUnicode')
        else:
            t = Template(index_tmpl, searchList=[namespace], filter='EncodeUnicode')

        output = [unicode(t).encode('utf-8')]

        return headers, output


if __name__ == "__main__":
    import os
    import optparse

    from paste.httpserver import serve

    parser = optparse.OptionParser()
    parser.add_option('-p', '--port', dest='port',
                      default=8080, type='int',
                      help="port to serve on (default 8080)")
    options, args = parser.parse_args()
                      
    # Get the app root. Defaults to current directory.
    pwd = os.environ['PWD']
    if not len(args) == 1: root = pwd
    else: root = os.path.join(pwd, args[0])

    app = DapServerApplication(root)
    serve(app, port=options.port, host='127.0.0.1')
