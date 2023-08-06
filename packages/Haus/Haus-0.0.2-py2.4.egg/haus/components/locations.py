""".. _LocationsComponent:

``locations`` -- Application Locations
======================================

Find common locations in the application.

"""

from haus.components.abstract import Component


class LocationsComponent(Component):

    provides = ['get_locations']

    def __init__(self, wrk):
        """Set up locations, relative paths considered from prefix."""
        locations = wrk.config.get('locations', {})
        for name, path in locations.items():
            if not path.startswith('/'):
                locations[name] = wrk.config['app']['prefix'] + "/" + path
        self.locations = locations
        wrk.functions['get_locations'] = self.get_locations 

    def get_locations(self, environ):
        return self.locations
