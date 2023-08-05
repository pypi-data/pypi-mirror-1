"""selector - WSGI delegation based on uri path and method.

(See the docstring of selector.Selector.)

Copyright (C) 2006 Luke Arno - http://lukearno.com/

This program is free software; you can redistribute it and/or modify 
it under the terms of the GNU General Public License as published by the 
Free Software Foundation; either version 2 of the License, or (at your 
option) any later version.

This program is distributed in the hope that it will be useful, but 
WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU 
General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program; if not, write to:

The Free Software Foundation, Inc., 
51 Franklin Street, Fifth Floor, 
Boston, MA  02110-1301, USA.

Luke Arno can be found at http://lukearno.com/

"""
import re
from itertools import starmap


def status_app(status, message=""):
    """Return a WSGI app that just returns the given status."""
    class WSGIApp:
        def __call__(self, environ, start_response):
            start_response(status, [])
            return [message or status]
    WSGIApp.__doc__ = "WSGI app that returns '%s'" % status
    return WSGIApp()


class Selector:
    """WSGI Middleware for request delegation.
    
    Delegation mapping structures take the following form:

    [(path_info_regex, {request_method: wsgi_app}), ...]

    Groups returned from regex are placed in environ['selector.vars'].
    path_info_regex may leave the '^' off of the beginning and use '^'
    as the prefix instead so that it is easy to switch prefixing
    schemes.

    declarative example:

    [(r'/hello/(?P<name>[a-zA-Z]+)', {'GET': say_hello})]

    say_hello in this case is a wsgi app that will find the name to
    say hello to in environ['selector.vars']['name']

    or you can just call add procedurally:

    selector.add(r'/hello/(?P<name>[a-zA-Z]+)', {'GET': say_hello})
    """
    
    method_not_supported = status_app('405 Method Not Supported')
    not_found = status_app('404 Not Found')
    
    def __init__(self, structure=None, prefix=""):
        """Initialize selector with optional mapping structure."""
        self.prefix = prefix
        self.mappings = []
        if structure is not None: self.slurp(structure)

    def slurp(self, structure):
        """Slurp in a mapping structure. See class docstring."""
        list(starmap(self.add, structure))

    def add(self, regex, method_dict):
        """Add a mapping."""
        regex = re.compile(self.prefix + regex)
        self.mappings.append((regex, method_dict))

    def __call__(self, environ, start_response):
        """Delegate request to the appropriate WSGI app."""
        app, environ['selector.vars'] = \
            self.select(environ['PATH_INFO'], environ['REQUEST_METHOD'])
        return app(environ, start_response)

    def select(self, path, method):
        """Figure out which app to delegate to or send 404 or 405."""
        for regex, method_dict in self.mappings:
            match = regex.search(path)
            if match:
                if method_dict.has_key(method):
                    return method_dict[method], match.groupdict()
                else:
                    return self.method_not_supported, {}
        return self.not_found, {}

