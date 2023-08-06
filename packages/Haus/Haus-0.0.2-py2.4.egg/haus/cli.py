"""Command Line Interface
======================

The :command:`haus` command comes with 2 subcommands.

--------------------
:command:`haus init` 
--------------------

- initialize a directory as a haus project:

.. code-block:: bash

    $ haus init --help
    usage: haus init package_name [target_dir]

    options:
      --version   show program's version number and exit
      -h, --help  show this help message and exit

-------------------
:command:`haus run` 
-------------------

- run via wsgiref for development:

.. code-block:: bash

    $ haus run  --help
    usage: haus run package_name host port

    options:
      --version             show program's version number and exit
      -h, --help            show this help message and exit
      -c CONFIG, --configs=CONFIG
                            Haus configuration files (comma separated).
      -r, --reload          Reload the package being run.
      -R RELOADLIST, --reloadlist=RELOADLIST
                            Reload packages that start with (comma seperated).

.. seealso::

   See the Quickstart_ for a breif example.

.. _Quickstart: quickstart.html

"""

import sys
from os.path import abspath
from optparse import OptionParser

from wsgiref.simple_server import make_server
from pkg_resources import iter_entry_points, \
                          Requirement, \
                          resource_filename 

from resolver import resolve
from memento import Assassin
from skel import Builder, StringTemplateFilter

from haus.core import Haus


run_usage = "%prog run package_name host port"


def report_error(parser, message):
    print message
    print
    parser.print_help()
    return 1


def run():
    parser = OptionParser(usage=run_usage, version="haus run 0.0.1")
    parser.add_option('-c', '--configs', dest='config',
                      help='Haus configuration files (comma separated).')
    parser.add_option('-r', '--reload', dest='reload', 
                      action='store_true', default=False,
                      help='Reload the package being run.')
    parser.add_option('-R', '--reloadlist', dest='reloadlist',
                      help='Reload packages that start with (comma seperated).')
    options, args = parser.parse_args()
    if len(args) == 3:
        package_name, host, port = args
        try:
            port = int(port)
        except ValueError, ve:
            return report_error(parser, "Port must be a number not "+repr(port))
        if options.config is None:
            configs = []
        else:
            configs = options.config.split(',')
        if options.reload or options.reloadlist:
            if options.reloadlist:
                to_reload = options.reloadlist.split(',')
            else:
                to_reload = [package_name]
            resolver_expression = "haus.core:Haus('%s'" % package_name
            if configs:
                resolver_expression += ", "
                resolver_expression += \
                    ", ".join("'%s'" % c for c in configs)
            resolver_expression += ")"
            application = Assassin(resolver_expression, to_reload)
        else:
            application = Haus(package_name, *configs)
        server = make_server(host, port, application)
        try:
            server.serve_forever()
        except KeyboardInterrupt, ki:
            print "Cheers, then!"
    else:
        return report_error(parser, "Wrong number of arguments.")


init_usage = "%prog init package_name [target_dir]"


def init():
    parser = OptionParser(usage=init_usage, version="haus init 0.1")
    options, args = parser.parse_args()
    if len(args) == 1:
        package_name = args[0]
        target_dir = '.'
    elif len(args) == 2:
        package_name, target_dir = args
    else:
        parser.print_help()
        return 1
    target_dir = abspath(target_dir)
    resource = Requirement.parse("haus")
    init_template = resource_filename(resource, 'haus/init')

    data = {'package_name': args[0]}
    builder = Builder(data, 
                      filters=[StringTemplateFilter()],
                      ignore=['.hg'])
    dirs, files = builder.build(init_template, target_dir)
    print dirs, "directories created."
    print files, "files written."


def main():
    """This is the Haus CLI."""
    if len(sys.argv) == 1:
        print "For help: haus [command] -h"
        print
        print "commands:"
        for entry_point in iter_entry_points('haus.commands'):
            print " "*4 +entry_point.name
    else:
        command = None
        for entry_point in iter_entry_points('haus.commands', sys.argv.pop(1)):
            command = entry_point.load()
        if command is None:
            print "Command not found."
            print
            return 1
        else:
            return command()


def command():
    sys.exit(main())


if __name__ == '__main__':
    command()
