"""Python Web Server Gateway Interface (WSGI) application and middleware.

This is an implementation of the DAP server as a WSGI application. This
allows the DAP server to be run on a variety of environments and combined
with third-party middleware (filters).

The module also offers an implementation of a THREDDS catalog generator
as a WSGI middleware, generating the catalog from the DAP server application. 
"""
