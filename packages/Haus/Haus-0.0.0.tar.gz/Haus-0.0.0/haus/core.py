""".. _HowHausWorks:

How Haus Works
==============

Haus composes multi-tiered WSGI middleware stacks.
There is an app-wide stack, a trunk stack, if you will,
that receives all incoming requests,
and branch stacks wrapping individual handlers to which 
the top of the trunk stack dispatchs. (You could have
multiple dispatchers and additional tiers of stacked 
middleware, but one is usually enough.)

--------
Stacking
--------

Stacks are created based on descriptors. A descriptor
is just a component name, or a 1, 2, or 3 tuple of
(component_name, args, kwargs)  or a list of stack
descriptors (but not nested). It describes a component
or a stack of components and what to call them with.
The middlewares returned by the components are then
applied in reverse order such that the leftmost
descriptor in a list is the outermost wrapper in the
stack.

.. code-block:: python

    stack = ['component1', ('component2`, ['foo'] {'bar':'baz'})]

----------------------------
Instantiating an Application
----------------------------

At the center of Haus is :class:`haus.core.Haus`. This class is
instantiated with the name or your Haus project (which is a 
just a regular Python package with a certain structure). An 
instance is a WSGI application for your WSGI server of choice. 
All additional arguements should be the names of config files. Haus
looks for configuration in your package, in :file:`mypackage/app.conf`
and merges all addition config files onto that, left to right. Basic 
config validation is done after the configs are parsed; you can 
extend the configuration requirements using the syntax for 
ConfigObj_ in your own :file:`mypackage/configspec.conf`. Then it 
loads the components, in the default order or the order specified 
in the configs. Components are loaded and the trunk stack is built.

.. code-block:: python

    from hause.core import Haus
    application = Haus('yourpackage', *list_of_config_files)

------------------
Loading Components
------------------

Components are found either in the config or through the 
*'haus.components'* entry point via pkg_resources. This means
you can add components with new names or overide the name
of existing component. Since components document the funcitons
they provide and consume in simple lists, creating components
is straight forward.

.. code-block:: ini

    [haus]
    app.stack = "['component1', ('component2`, ['foo'] {'bar':'baz'})]"
    load.order = component1, component2, component3, component4

    [haus.components]
    component4 = mypackage.mymodule:ComponentClass

----------------
Stack Components
----------------

After other components are loaded, composite components
are created using stack descriptors based on configs.
This means that you can combine `sessions` and `cache`,
for instance, and just call it `state`. It would look
like this in your config:

.. code-block:: ini

    [haus.stacks]
    component5 = "['component3', ('component4', ['foo'])]"

-------------------
Framework Functions
-------------------

As components are loaded they will register the functions
they provide in the :attr:`haus.core.Haus.functions`
dictionary. This dictionary is used by other components and
handlers to access funtionality. Most of these take just
environ, some of them are WSGI apps, such as those that 
send HTTP status. These functions are available to handlers,
even if they are WSGI apps, via ``environ['haus.functions']``,
thanks to the **standard** component.
By default, the Yaro component exposes these via ``req.ff``.

.. code-block:: python

    @tack('somestack')
    def isit(req):
        if req.ff == req.environ['haus.functions']:
            return "It is!"
        else:
            return "It is not!"

---------------
The Trunk Stack
---------------

Finally the "app stack" is created by calling the components
listed in the config. This is the app-wide middleware stack
that usually terminates in the dispatcher. The dispatcher
then dispatches to brach stack wrapped handlers.
 
------------------------
Branch Stacks with @tack
------------------------

Your handlers can simply be decorated with 
:func:`haus.core.tack`, which will attach the given
stack descriptor to your handler. A middleware stack
is applied to your handler based on this descriptor
only when it is loaded by the dispather. This keeps
your handlers from getting burried in middleware so 
that you can unit test them.

-----------------------------------
Why the Stacks and not Just Layers?
-----------------------------------

There are going to be some components that need request handler-specific 
parameters: ("allowed_roles" need to be provided per-handler for the 
access control layer to provide the granularity sufficient to achieve
any usefulness. The templating layer needs to know which template to use 
for a given handler, what the "view" is for a given "controller," if you 
will.) Maintaining these verticle links binding stacks of components 
together, through what could otherwise be understood as a horizontally 
layered architecture, is a tax paid  on the luxury of centrallizing 
cross-cutting concerns (like dispatch or security) without surrendering 
to a single, inevitably klunky and/or rigid mega-stack built to rule 
them all.
"""

import sys

from pkg_resources import iter_entry_points, \
                          Requirement, \
                          resource_filename
from configobj import ConfigObj, flatten_errors
from validate import Validator

# This is just a hack for Python2.4 (no functools).
from haus.components.abstract import update_wrapper


def make_spec(filename): 
    return ConfigObj(
        filename,
        encoding='UTF-8',
        list_values=False
    )


def config_error_messages(config, result):
    errors = []
    for entry in flatten_errors(config, result):
        section_list, key, error = entry
        if key is not None:
           section_list.append(key)
        else:
            section_list.append('[missing section]')
        section_string = ', '.join(section_list)
        if error == False:
            error = 'Missing value or section.'
        errors.append(section_string + ' = ' + str(error))
    return errors


def tack(stack_descriptor, *args, **kwargs):
    """Decorate callable with metadata for stackify.

    See :meth:`haus.core.Haus.stackify`.
    """
    def deco(app):
        app.haus_metadata = (stack_descriptor, args, kwargs)
        return app
    return deco


class BadStackDescriptorError(Exception): pass


class Haus(object):
    """The framework."""

    def __init__(self, package_name, *config_files):
        """Load config, load components and create the base app stack."""
        self.package_name = package_name
        self.package_resource = Requirement.parse(self.package_name)
        self.haus_resource = Requirement.parse('haus')
        self.functions = {}
        self.load_config(*config_files)
        self.load_components()
        self.app = self.stack(eval(self.config['haus']['app.stack']))(self)

    def pdfilename(self, filename):
        """Use pkg_resources to get package data filenames."""
        return resource_filename(
            self.package_resource, 
            self.package_name + '/' + filename
        )

    def hauspdfilename(self, filename):
        """Use pkg_resources to get haus package data filenames."""
        return resource_filename(
            self.haus_resource,
            'haus/' + filename
        )

    def load_config(self, *config_files):
        """Load up the app configuration."""
        config_spec = make_spec(self.hauspdfilename('configspec.conf'))
        try:
            config_spec.merge(make_spec(self.pdfilename('configspec.conf')))
        except KeyError, ke:
            pass
        config_files = list(config_files)
        config_files.insert(0, self.pdfilename('app.conf'))
        self.config = reduce(
            lambda x, y: x.merge(y) or x,
            (ConfigObj(f, configspec=config_spec) for f in config_files)
        )
        result = self.config.validate(Validator(), preserve_errors=True)
        if result is True:
            return self.config
        else:
            messages = config_error_messages(self.config, result)
            for message in messages:
                print >> sys.stderr, message
            sys.exit(1)

    def load_components(self):
        """Load the framework components."""
        components = {}
        config_components = self.config.get('haus.components', {})
        config_stacks = self.config.get('haus.stacks', {})
        for name in self.config['haus']['load.order']:
            if name in config_components:
                components[name] = resolve(config_components[name])(self)
            else:
                for entry_point in iter_entry_points('haus.components', name):
                    components[name] = entry_point.load()(self)
        self.components = components
        for name, descriptor_string in config_stacks.items():
            components[name] = self.stack_component(eval(descriptor_string))

    def stack(self, stack_descriptor, *args, **kwargs):
        """Build a middleware that applies."""
        if isinstance(stack_descriptor, (str, unicode, tuple)):
            stack_descriptor = [stack_descriptor]
        def stack_middleware(app):
            """Call with None when loading the base stack"""
            for component in reversed(stack_descriptor):
                if isinstance(component, (str, unicode)):
                    mw = self.components[component](self, *args, **kwargs)
                elif isinstance(component, tuple) and len(component) == 2:
                    mw = self.components[component[0]](self, *component[1], **kwargs)
                elif isinstance(component, tuple) and len(component) == 3:
                    mw = self.components[component[0]](self, *component[1], **component[2])
                else:
                    raise BadStackDescriptorError("Stack: "+str(stack_descriptor)+" Component: "+str(component))
                app = mw(app)
            return app
        return stack_middleware

    def stack_component(self, stack_descriptor):
        """Return a component that produces middleware for the descriptor."""
        def component(wrk, *args, **kwargs):
            return self.stack(stack_descriptor, *args, **kwargs)
        return component

    def stackify(self, app):
        """Wrap with stack according to app.haus_metadata.

        The "metadata" is really 3 tuple that is used to call self.stack().
        This will just fall through if the attribute does not exist.
        """
        if not hasattr(app, 'haus_metadata'):
            return app
        stack_descriptor, args, kwargs = app.haus_metadata
        if args is None:
            args = []
        if kwargs is None:
            kwargs = {}
        newapp = self.stack(stack_descriptor, *args, **kwargs)(app)
        return update_wrapper(newapp, app)

    def __call__(self, environ, start_response):
        """Call the application."""
        return self.app(environ, start_response)
