The Data Access Protocol (DAP) is a data transmission protocol
designed specifically for science data. The protocol relies on the
widely used HTTP and MIME standards, and provides data types to
accommodate gridded data, relational data, and time series, as well
as allowing users to define their own data types.

This module implements a DAP client that can access remote datasets
stored in DAP servers. The client downloads metadata describing the
datasets, and builds array-like objects that act as proxies for the
data. These objects download the data from the server transparently
when necessary.

The module also implements a DAP server, able to serve data from
different formats through a plugin architecture. The server is
implemented as a WSGI application, and can be run on a variety of
servers: as a CGI script; with Twisted and mod_python; or even as
a ISAPI extension under IIS; for example.

For more information on the DAP, visit http://opendap.org/.

(c) 2003-2006 Roberto De Almeida <rob@pydap.org>
http://pydap.org/
