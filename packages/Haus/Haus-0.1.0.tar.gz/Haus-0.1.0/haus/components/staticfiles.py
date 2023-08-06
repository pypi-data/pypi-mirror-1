""".. _StaticFilesComponent:

``static`` -- Static Content
============================

Uses  Static_ to serve up static content.
Provides a framework function that gets used
by selector when it is present.

.. _Static: http://lukearno.com/projects/static/

"""

from static import Cling

from haus.components.abstract import Component, update_wrapper


class StaticClingComponent(Component):

    provides = ['static_app']

    def __init__(self, wrk):
        cling = Cling(wrk.pdfilename(wrk.config['static']['root']))
        cling.not_found = wrk.functions['status404']
        cling.method_not_allowed = wrk.functions['status405']
        wrk.functions['static_app'] = cling

