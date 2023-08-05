"""A simple WSGI logging middleware."""

import logging


def make_logger_filter(global_conf, **kwargs):
    def filter(app):
        return LoggerMiddleware(app, **kwargs)
    return filter


class LoggerMiddleware(object):
    def __init__(self, app,
                       level=None,
                       format='%(asctime)s %(levelname)s %(message)s',
                       filemode='w',
                       **kwargs):
        self.app = app

        if level is None:
            level = logging.DEBUG
        else:
            # Level can be a number or 'debug', 'INFO', 'Error', etc.
            try:
                level = int(level)
            except ValueError:
                level = getattr(logging, level.upper())

        # Configure logger.
        logging.basicConfig(level=level,
                            format=format,
                            filemode=filemode,
                            **kwargs)
        self.logger = logging
    
    def __call__(self, environ, start_response):
        environ['logger'] = self.logger
        return self.app(environ, start_response)
