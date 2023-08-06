""".. _StaticFilesComponent:

``static`` -- Static Content
============================

Uses Static_ to serve up static content.

.. _Static: http://lukearno.com/projects/static/

"""

from static import Cling

from haus.components.abstract import Component, update_wrapper


class StaticClingComponent(Component):

    def __call__(self, wrk, *args, **kwargs):
        def middleware(app):
            cling = Cling(wrk.pdfilename(wrk.config['static']['root']))
            cling.not_found = cling.method_not_allowed = app
            return update_wrapper(cling, app)
        return middleware

