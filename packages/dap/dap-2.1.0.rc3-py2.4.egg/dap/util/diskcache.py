"""A simple disk cache middleware."""

# TODO: check headers for expiration.

import os
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
            # Output and store at the same time.
            app = self.app(self.environ, self._start)
            body = []
            for line in app:
                yield line
                body.append(line)
            obj = self.status, self.response_headers, body
            self.db['key'] = pickle.dumps(obj, 2)

            # Close app?
            if hasattr(self.app, 'close'): self.app.close()

        else:
            status, response_headers, body = pickle.loads(obj)
            self.start(status, response_headers)
            for line in body:
                yield line

    def _start(self, status, response_headers):
        self.start(status, response_headers)
        self.status = status
        self.response_headers = response_headers

    def close(self):
        self.db.close()
