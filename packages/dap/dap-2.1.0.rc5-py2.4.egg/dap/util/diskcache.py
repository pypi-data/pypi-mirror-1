"""A simple disk cache middleware."""

__author__ = 'Roberto De Almeida <rob@pydap.org>'

import os
import time
import anydbm 

try:
    import cPickle as pickle
except ImportError:
    import pickle

from dap.helper import construct_url


def make_diskcache_filter(global_conf, storage, flush='True', **kwargs):
    if flush.lower() == 'true': flush = True
    elif flush.lower() == 'false': flush = False
    else: flush = int(flush)

    def filter(app):
        return DiskCacheMiddleware(app, storage, flush, **kwargs)
    return filter


class DiskCacheMiddleware(object):
    def __init__(self, app, storage, flush=True, **kwargs):
        self.app = app

        # Flush db?
        if flush:
            mode = 'n'
        else:
            mode = 'c'

        self.db = anydbm.open(storage, mode)

    def __call__(self, environ, start_response):
        self.environ = environ
        self.start = start_response

        return self

    def __iter__(self):
        key = construct_url(self.environ)
        obj = self.db.get(key)
        if not obj:
            # Run app and possibly store output.
            return self._run_app()
        else:
            # Possibly read from cache.
            status, response_headers, body = pickle.loads(obj)
            
            # Check if expired.
            expiration = get_expiration(response_headers)
            if expiration and expiration < time.gmtime():
                del self.db[key]
                return self._run_app()
            else:
                return self._read_cache(status, response_headers, body)

    def _read_cache(self, status, response_headers, body):
        self.start(status, response_headers)
        for line in body:
            yield line

    def _run_app(self):
        # Output and store at the same time.
        app = self.app(self.environ, self._start)
        body = []
        for line in app:
            yield line
            body.append(line)

        # Check if expired.
        expiration = get_expiration(self.response_headers)
        if not expiration or expiration > time.gtime():
            obj = self.status, self.response_headers, body
            self.db['key'] = pickle.dumps(obj, 2)

        # Close app?
        if hasattr(self.app, 'close'): self.app.close()

    def _start(self, status, response_headers):
        self.start(status, response_headers)
        self.status = status
        self.response_headers = response_headers

    def close(self):
        self.db.close()


def get_expiration(headers):
    expiration = [header[1] for header in headers if header[0].lower() == 'expires']
    expiration.sort()  # just in case there are more than one header, use the earliest.
    if expiration:
        return time.strptime(expiration[0], "%a, %d %b %Y %H:%M:%S GMT")
