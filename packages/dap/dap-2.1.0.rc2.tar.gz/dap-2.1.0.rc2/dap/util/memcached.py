"""A simple memcache middleware."""

import memcache

from dap.helper import construct_url


def make_memcached_filter(global_conf, clients, **kwargs):
    # Transform into list.
    clients = clients.split(',')
    clients = [client.strip() for client in clients]
    
    def filter(app):
        return MemcachedMiddleware(app, clients, **kwargs)
    return filter


class MemcachedMiddleware(object):
    def __init__(self, app, clients, debug=0, flush=True, **kwargs):
        self.app = app
        self.mc = memcache.Client(clients, debug=debug)

        # Flush db.
        if flush: self.mc.flush_all()

    def __call__(self, environ, start_response):
        self.environ = environ
        self.start = start_response

        return self

    def __iter__(self):
        key = construct_url(self.environ)
        obj = self.mc.get(key)
        if not obj:
            # Output and store at the same time.
            app = self.app(self.environ, self._start)
            body = []
            for line in app:
                yield line
                body.append(line)
            obj = self.status, self.response_headers, body
            self.mc.set(key, obj)

            # Close app?
            if hasattr(self.app, 'close'): self.app.close()

        else:
            status, response_headers, body = obj
            self.start(status, response_headers)
            for line in body:
                yield line

    def _start(self, status, response_headers):
        self.start(status, response_headers)
        self.status = status
        self.response_headers = response_headers
