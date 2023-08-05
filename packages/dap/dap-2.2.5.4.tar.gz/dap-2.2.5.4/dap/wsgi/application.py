"""DAP server WSGI application.

This module implements a DAP server over the WSGI specification. For more
information, read http://www.python.org/peps/pep-0333.html.
"""

__author__ = "Roberto De Almeida <rob@pydap.org>"

import sys
import os
import re
import urllib

from paste.httpexceptions import HTTPException, HTTPNotFound
from paste.request import construct_url
from paste.deploy.converters import asbool
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
        self.environ = environ
        self.start = start_response
        return self

    def __iter__(self):
        status = '200 OK'
        try:
            response_headers, output = self.handlerequest()
        except HTTPException:
            # Raise these exceptions so they get 
            # captured by the middleware.
            raise
        except:
            status = '500 Internal Error'
            self.handler = BaseHandler(environ=self.environ)
            response_headers, output = self.handler.error(sys.exc_info())
            if asbool(self.environ.get('x-wsgiorg.throw_errors')): raise

        self.start(status, response_headers)
        for line in output:
            yield line

    def handlerequest(self):
        # Remove the leading '/'.
        request = self.environ.get('PATH_INFO', '').lstrip('/')
        request = urllib.unquote(request)

        if not request:
            # Show list of responses.
            message = ['<a href="/.%s">%s</a>' % (ep.name, ep.name) for ep in iter_entry_points("dap.response")]
            message = ' | '.join(message)
            self.handler = BaseHandler(environ=self.environ)
            response = self.handler.help(message=message)
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
    def __init__(self, root, name="pyDAP server", template=None, verbose=False, **kwargs):
        # Ensure that root ends with /.
        if not root.endswith('/'): root = '%s/' % root
        
        self.root = root
        self.name = name
        self.template = template

        # Set verbose option and additional keywords.
        dap.lib.VERBOSE = asbool(verbose)
        self.to_environ = kwargs

        # And load plugins for data handling.
        self.plugins = loadplugins()

    def handlerequest(self):
        # Update environ with user-defined keys.
        self.environ.update(self.to_environ)

        # Remove the leading '/'.
        request = self.environ.get('PATH_INFO', '').lstrip('/')
        request = urllib.unquote(request)

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
        response = call(self.environ.get('QUERY_STRING'))

        return response

    def listfiles(self, dir):
        headers = [('XDODS-Server', 'dods/%s' % '.'.join([str(i) for i in dap.lib.__dap__])),
                   ('Content-Type', 'text/html'),
                   ('Content-Encoding', 'utf-8'), ]

        location = construct_url(self.environ, with_query_string=False)
        location = location.rstrip('/')
        title = 'DODS directory for %s' % location

        # Check which files are supported by plugins.
        res = [plugin.extensions for plugin in self.plugins]
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
