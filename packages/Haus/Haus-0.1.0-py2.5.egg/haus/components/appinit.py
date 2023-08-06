""".. _AppInitComponent:

``appinit`` -- Application Initialization
=========================================

If your package has an ``init()`` function, this will
try to call it with the :class:`haus.core.Haus` instance.
By default, his is the very last builtin component run.

"""


from haus.components.abstract import Component

from resolver import resolve


class AppInitComponent(Component):

    def __init__(self, wrk):
        try:
            init = resolve(wrk.package_name+":init")
            init(wrk)
        except (ImportError, AttributeError), err:
            pass

