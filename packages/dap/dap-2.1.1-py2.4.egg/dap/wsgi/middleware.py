"""DODS related WSGI middleware."""

__author__ = "Roberto De Almeida <rob@pydap.org>"

import os
import locale
from xml.dom.minidom import Document, ProcessingInstruction

try:
    from xml.dom.ext import PrettyPrint
except ImportError:
    PrettyPrint = None

try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO

from dap import dtypes
from dap.plugins import loadhandler
from dap.exceptions import ExtensionNotSupportedError
from dap.helper import construct_url


def make_catalog_filter(global_conf, **kwargs):
    def filter(app):
        return ThreddsCatalogMiddleware(app, **kwargs)
    return filter


class ThreddsCatalogMiddleware(object):
    """THREDDS Catalog builder.

    This middleware builds a catalog.xml file following the THREDDS
    specification. The catalog describes the datasets being served by the
    DAP server passed as a WSGI application.

    For specs:
        http://www.unidata.ucar.edu/projects/THREDDS/tech/catalog/InvCatalogSpec.html

    Validate with:
        http://motherlode.ucar.edu:8080/thredds/validateForm.html
    """
    def __init__(self, app, location='/catalog.xml', stylesheet=None):
        self.app = app
        self.location = location
        self.stylesheet = stylesheet

        # Get name from app.
        self.name = getattr(self.app, 'name', 'pyDAP server')

    def __call__(self, environ, start_response):
        if environ['PATH_INFO'] == self.location:
            self.environ = environ
            self.start = start_response

            # Create catalog.
            self.doc = Document()

            # Add stylesheet.
            if self.stylesheet is not None:
                proc = ProcessingInstruction('xml-stylesheet', 'href="%s" type="text/xsl"' % self.stylesheet)
                self.doc.appendChild(proc)
            
            catalog = self.doc.createElementNS("http://www.unidata.ucar.edu/namespaces/thredds/InvCatalog/v1.0", "catalog")
            self.doc.appendChild(catalog)

            # Add main service.
            service = self.doc.createElement("service")
            service.setAttribute("name", self.name)
            service.setAttribute("serviceType", "DODS")
            catalog.appendChild(service)
            
            return self
        else:
            return self.app(environ, start_response)
            
    def __iter__(self):
        self.status = "200 OK"
        response_headers, output = self._build_catalog()

        self.start(self.status, response_headers)
        for line in output:
            yield line

    def _build_catalog(self):
        # Add base URL.
        base = construct_url(self.environ, with_query_string=False)
        base = base[:-(len(self.location)-1)]  # remove /catalog.xml from url
        service = self.doc.getElementsByTagName('service')[0]
        service.setAttribute("base", base)

        files = []
        for root, dir_, files_ in os.walk(self.app.root):
            for file_ in files_:
                path = os.path.join(root, file_)
                files.append(path)

        # Add files that are handled by the plugins.
        for file_ in files:
            try:
                H = loadhandler(file_, self.environ, self.app.plugins)
                # TODO: add try: ... except: ... here
                dataset = H._parseconstraints()
                name = H.description
                #urlPath = file_[len(self.app.root)+1:]
                urlPath = file_[len(self.app.root):]
                
                # Build the dataset XML.
                self._build_dataset(dataset, name, urlPath)
                
                # Close handler.
                if hasattr(H, 'close'): H.close()
            except ExtensionNotSupportedError:
                pass

        headers = [
                   ('Content-type', 'application/xml; charset=utf-8'),
                  ]

        output = StringIO()
        if PrettyPrint is not None:
            PrettyPrint(self.doc, stream=output, indent='    ')
        else:
            catalog = self.doc.getElementsByTagName('catalog')[0]
            catalog.setAttribute("xmlns", "http://www.unidata.ucar.edu/namespaces/thredds/InvCatalog/v1.0")
            output.write(self.doc.toprettyxml(indent='    '))
        output.seek(0)

        return headers, output

    def _build_dataset(self, dataset, name, urlPath):
        catalog = self.doc.getElementsByTagName('catalog')[0]
        service = self.doc.getElementsByTagName('service')[0]

        dataset_ = self.doc.createElement("dataset")
        dataset_.setAttribute("serviceName", service.getAttribute("name"))
        dataset_.setAttribute("name", name)
        dataset_.setAttribute("urlPath", urlPath)
        catalog.appendChild(dataset_)

    def close(self):
        if hasattr(self.app, 'close'): self.app.close()
