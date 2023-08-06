""".. _SessionsandCachingComponent:

``sessions``, ``cache`` -- Sessions and Caching
===============================================

Sessions and caching are provided trough Beaker_,
which provides an excellent array of storage
options. See :ref:`Configuring`.

.. _Beaker: <http://beaker.groovie.org/>

"""

from beaker.middleware import SessionMiddleware, CacheMiddleware

from haus.components.abstract import Component, wraps, update_wrapper


class BeakerSessionsComponent(Component):

    provides = ['get_session', 'invalidate_session']

    def __init__(self, wrk):
        wrk.functions['get_session'] = self.get_session
        wrk.functions['invalidate_session'] = self.invalidate_session
        config = wrk.config.get('sessions', {})
        self.environ_key = \
            str(config.get('environ_key', wrk.package_name + '.session'))
        
    def get_session(self, environ):
        return environ.get(self.environ_key)

    def invalidate_session(self, environ):
        session = self.get_session(environ)
        return session.invalidate()

    def __call__(self, wrk, *args, **kwargs):
        config = wrk.config['sessions']
        #if not config.get('data_dir', '/').startswith('/'):
        #    config['data_dir'] = wrk.pdfilename(config['data_dir'])
        config = dict((str(k), str(v)) for k, v in config.iteritems())
        config.update(kwargs)
        config = dict(("session."+k, v) for k, v in config.iteritems())
        def middleware(app):
            @wraps(app)
            def proxy(environ, start_response):
                # TODO: So, session change during itereation of the iterator
                #       returned (when that is the case) would not be saved?
                try:
                    ret = app(environ, start_response)
                finally:
                    session = self.get_session(environ)
                    session.save()
                return ret
            newapp = SessionMiddleware(
                proxy, 
                environ_key=self.environ_key,
                config=config
            )
            newapp.__name__ = app.__name__
            return newapp
        return middleware


class BeakerCacheComponent(Component):

    provides = ['get_cache']

    def __init__(self, wrk):
        wrk.functions['get_cache'] = self.get_cache
        config = wrk.config.get('cache', {})
        self.environ_key = str(
            config.get('environ_key', wrk.package_name + '.cache')
        )

    def get_cache(self, environ):
        return environ.get(self.environ_key)

    def __call__(self, wrk, *args, **kwargs):
        config = wrk.config['cache']
        config = dict((str(k), str(v)) for k, v in config.iteritems())
        config.update(kwargs)
        config = dict(("cache."+k, v) for k, v in config.iteritems())
        def middleware(app):
            newapp = CacheMiddleware(
                app, 
                environ_key=self.environ_key, 
                config=config
            )
            newapp.__name__ = app.__name__
            return newapp
            return update_wrapper(newapp, app)
        return middleware

