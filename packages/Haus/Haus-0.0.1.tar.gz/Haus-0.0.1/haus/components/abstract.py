""".. _ComponentConcepts:

Component Concepts
==================

Components do pretty much everything in Haus.
Components are passed the configured framework
instance (:class:`haus.core.Haus`) during its 
own initialization and again
whenever it calls the Component instance to generate
middleware for stack composition. Stacking is
explained in detail in :ref:`HowHausWorks`.

Haus encourages the use of :mod:`functools` to 
create well behaved decorators and you can get
them through here when writing components, if
you want the Python 2.4 compatibility.
This module also provides a :func:`update_wrapper` and
:func:`wraps`, which come from :mod:`functools` in 
Python 2.5 and higher, but will provide it's own 
implementation for Python 2.4.

.. seealso::

    See also: :ref:`How Haus Works`
"""

# This little bit is a hack for the sake of Python2.4:

try:
    from functools import wraps, update_wrapper, \
                          WRAPPER_ASSIGNMENTS, WRAPPER_UPDATES
except ImportError, ie:

    WRAPPER_ASSIGNMENTS = ('__module__', '__name__', '__doc__')
    WRAPPER_UPDATES = ('__dict__',)

    def update_wrapper(wrapper, wrapped, assigned=None, updated=None):
        if assigned is None:
            assigned = WRAPPER_ASSIGNMENTS
        if updated is None:
            updated = WRAPPER_UPDATES
        for attr in assigned:
            setattr(wrapper, attr, getattr(wrapped, attr))
        for attr in updated:
            getattr(wrapper, attr).update(getattr(wrapped, attr))
        return wrapper

    def wraps(wrapped, assigned=None, updated=None):
        def proxy(wrapper):
            return update_wrapper(wrapper, wrapped, assigned, updated)
        return update_wrapper(proxy, wrapped)


class HausComponentError(Exception): pass

class Component(object):
    """Abstract base class for haus components."""

    provides = []
    consumes = []

    def __init__(self, wrk):
        """Stuff that happens when the application is loaded.

        Register functions on the framework instance, 
        initialize this component at load time...
        Be aware that often you must load those components 
        which provide framework functions before those which
        consume them. This is a do-nothing by default.
        """

    def __call__(self, wrk, *args, **kwargs):
        """Provide wrapper when individual handler is loaded.

        In other words, this function is used by the stacker
        to get the middleware to stack. How to provide that 
        is totally up to the component. If this is not 
        implemented for a component and you try to stack
        it, it will raise a :class:`HausComponentError`.
        """
        raise HausComponentError(
            "Component %s does cannot be stacked."
            % self.__name__
        )
