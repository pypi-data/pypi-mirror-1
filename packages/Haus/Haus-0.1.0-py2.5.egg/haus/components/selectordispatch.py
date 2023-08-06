""".. _SelectorComponent:

``selector`` -- Request Dispatcher
==================================

Dispatch request based on your :file:`urls.map`
using Selector_

.. _Selector: http://lukearno.com/project/selector/

"""

from selector import Selector

from haus.components.abstract import Component


class SelectorComponent(Component):
    """Terminates a stack with selector for dispatch."""

    consumes = ['status404', 'status405']
    provides = ['get_selector']

    def __init__(self, wrk):
        self.selector = None
        wrk.functions['get_selector'] = self.get_selector

    def get_selector(self, environ):
        """Return the selector instance for this app instance."""
        return self.selector

    def __call__(self, wrk, *args, **kwargs):
        if self.selector is None:
            selector = Selector()
            selector.__name__ = wrk.package_name
            selector.wrap = wrk.stackify
            if 'login_page' in wrk.functions:
                login_page = wrk.functions['login_page']
                selector.add("/login/", GET=login_page, POST=login_page)
            if 'logout_page' in wrk.functions:
                logout_page = wrk.functions['logout_page']
                selector.add("/logout/", GET=logout_page)
            if 'static_app' in wrk.functions:
                static_app = wrk.functions['static_app']
                selector.add("/_static|", GET=static_app, HEAD=static_app)
            mapfile = wrk.pdfilename(str(wrk.config['selector']['map']))
            selector.slurp_file(mapfile)
            selector.status404 = wrk.functions['status404']
            selector.status405 = wrk.functions['status405']
            self.selector = selector
        def middleware(app):
            return self.selector
        return middleware

