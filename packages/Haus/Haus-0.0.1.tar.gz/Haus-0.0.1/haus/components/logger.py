""".. _LoggingComponent:

``logger`` -- Application Logging
=================================

Provide a logger. Goes to ``sys.stderr``.

TODO: Expand the configuration options and stick
to standard library options as much as possible.

"""

import sys, logging

from haus.components.abstract import Component, wraps, update_wrapper


class LoggingComponent(Component):

    provides = ['get_logger']
    consumes = ['get_logger', 'status500']

    def __init__(self, wrk):
        self.package_name = wrk.package_name
        self.logger = None
        config = wrk.config.get('logging', {})
        level = config.get('level', 'DEBUG')
        self.level = getattr(logging, level)
        default_format = "[%(name)s:%(levelname)s:%(module)s][%(asctime)s] %(message)s"
        self.format = config.get('format', default_format)
        wrk.functions['get_logger'] = self.get_logger

    def get_logger(self, environ):
        if self.logger is None:
            logger = logging.getLogger(self.package_name)
            logger.setLevel(self.level)
            if logger.handlers == []:
                handler = logging.StreamHandler(sys.stderr)
                handler.setLevel(self.level)
                if self.format is not None:
                    formatter = logging.Formatter(self.format)
                    handler.setFormatter(formatter)
                logger.addHandler(handler)
            self.logger = logger
        return self.logger

    def __call__(self, wrk, *args, **kwargs):
        def middleware(app):
            @wraps(app)
            def proxy(environ, start_response):
                logger = wrk.functions['get_logger'](environ)
                start_response_called = [False]
                def new_start_response(a, b, c=None):
                    start_response_called[0] = True
                    return start_response(a, b, c)
                update_wrapper(new_start_response, start_response)
                try:
                    return app(environ, new_start_response)
                except Exception, e:
                    logger.exception(e)
                    if not start_response_called[0]:
                        return wrk.functions['status500'](environ, start_response)
                    else:
                        return wrk.functions['status500'](
                            environ, 
                            lambda a, b, c=None: None
                        )
            return proxy
        return middleware
