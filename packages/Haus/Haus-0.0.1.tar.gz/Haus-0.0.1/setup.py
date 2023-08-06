"""setup - setuptools based setup for Haus

Copyright (C) 2006-2008 Luke Arno - http://lukearno.com/

This library is free software; you can redistribute it and/or
modify it under the terms of the GNU Lesser General Public
License as published by the Free Software Foundation; either
version 2.1 of the License, or (at your option) any later version.

This library is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
Lesser General Public License for more details.

You should have received a copy of the GNU Lesser General Public
License along with this library; if not, write to:

The Free Software Foundation, Inc., 
51 Franklin Street, Fifth Floor, 
Boston, MA  02110-1301, USA.

Luke Arno can be found at http://lukearno.com/

"""

import os

import ez_setup
ez_setup.use_setuptools()

from setuptools import setup, find_packages

setup(name='Haus',
      version='0.0.1',
      description=\
        'A loosely joined WSGI-centric Web programming framework.',
      long_description="""\
It is easy to add components to the framework or override components 
with your own versions on a per application basis. You can control how 
components are loaded and applied to your application by adding simple 
configuration options. The framework is connected to your application 
code and templates with an easy-to-use decorator.
      """,
      author='Luke Arno',
      author_email='luke.arno@gmail.com',
      url='http://houseofhaus.org/',
      license="LGPL",
      packages=find_packages(),
      install_requires="""
        wsgiref
        Genshi==0.5
        Beaker
        ConfigObj==4.5.2
        selector
        static
        yaro
        barrel>=0.1.3
        skel
        resolver
        memento
      """,
      entry_points = """
          [console_scripts]
              haus=haus.cli:main
          [haus.commands]
              init=haus.cli:init
              run=haus.cli:run
          [haus.components]
              prefixer=haus.components.prefixer:PrefixerComponent
              selector=haus.components.selectordispatch:SelectorComponent
              static=haus.components.staticfiles:StaticClingComponent
              yaro=haus.components.yaroreq:YaroComponent
              standard=haus.components.standard:StandardFunctionsComponent
              status=haus.components.status:HTTPStatusComponent
              genshi=haus.components.genshiview:GenshiTemplatingComponent
              logger=haus.components.logger:LoggingComponent
              sessions=haus.components.beakerstate:BeakerSessionsComponent
              cache=haus.components.beakerstate:BeakerCacheComponent
              barrel=haus.components.barrelsec:BarrelSecurityComponent
              locations=haus.components.locations:LocationsComponent
              appinit=haus.components.appinit:AppInitComponent
      """,
      include_package_data=True,
      keywords="wsgi web http framework rest",
      classifiers=['Development Status :: 3 - Alpha',
                   'Environment :: Web Environment',
                   'Intended Audience :: Developers',
                   'License :: OSI Approved :: GNU Library or Lesser General Public License (LGPL)',
                   'Natural Language :: English',
                   'Operating System :: OS Independent',
                   'Programming Language :: Python',
                   'Topic :: Software Development :: Libraries',
                   'Topic :: Utilities'])

