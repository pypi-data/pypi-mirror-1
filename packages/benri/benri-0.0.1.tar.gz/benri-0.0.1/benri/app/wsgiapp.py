# -*- coding: iso-8859-15 -*-
# (c) Mikael Högqvist

class WSGIApp(object):

    def routes_get(self):
        """Returns a list compatible with `selector.slurp`.
        """
        if hasattr(self, '_routes'):
            return [(key, self._routes[key]) for key in self._routes.keys()]

        # probably a filter app if routes have not been defined
        return []

    def routes_set(self, value):
        self._routes = value

    def routes_del(self):
        del self._routes
                
    routes = property(routes_get, routes_set, routes_del, routes_get.__doc__)

