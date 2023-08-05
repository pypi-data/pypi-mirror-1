# -*- coding: latin-1 -*-
"""selector - WSGI delegation based on URL path and method.

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

    Declarative example:

    [(r'/hello/(?P<name>[a-zA-Z]+)', {'GET': say_hello})]

    say_hello in this case is a wsgi app that will find the name to
    say hello to in environ['selector.vars']['name']

    Or you can just call add procedurally:

    selector.add(r'/hello/(?P<name>[a-zA-Z]+)', {'GET': say_hello})
    selector.add(r'/foo$', GET=get_foo)

    If you mix a dict and **kwars like this:

    selector.add(r'/bar$', {'GET': old_bar}, GET=new_bar)

    new_bar wins (**kwars override).
    
    Note:

    As of version 0.04a Selector has a url_syntax_parser member that
    preprocesses the path_info_regex (so in fact, it no longer needs to 
    be a regex, but something that your parser can make a regex from.)

    The 'parser' keyword arg of __init__ sets this member.
    
    The 'parser' keyword arg of slurp also sets this member but resets
    it to its previous value when the slurp is complete.

    See the SimpleSyntaxParser class in this module for a simple and
    handy syntax parser.  The defalt parser is a do nothing.
    """
    
    method_not_supported = status_app('405 Method Not Supported')
    not_found = status_app('404 Not Found')
    
    def __init__(self, structure=None, prefix="", parser=lambda x: x):
        """Initialize selector with optional mapping structure."""
        self.prefix = prefix
        self.mappings = []
        self.url_syntax_parser = parser
        if structure is not None: self.slurp(structure)

    def slurp(self, structure, parser=None):
        """Slurp in a mapping structure. See class docstring."""
        if parser is not None:
            oldparser = self.url_syntax_parser
            self.url_syntax_parser = parser
        list(starmap(self.add, structure))
        if parser is not None:
            self.url_syntax_parser = oldparser

    def add(self, regex, method_dict=None, **http_methods):
        """Add a mapping."""
        # Thanks to Sébastien Pierre 
        # for suggesting that this accept keyword args.
        if method_dict is None:
            method_dict = {}
        method_dict = dict(method_dict)
        method_dict.update(http_methods)
        regex = self.url_syntax_parser(self.prefix + regex)
        regex = re.compile(regex)
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


class SimpleSyntaxParser(object):
    """Callable to turn URL patterns into regexes with named groups.
    
    For instance /hello/{name} becomes ^\/hello\/(?P<name>\w+)$
    """

    start, end = '{}'

    def lookup(self, name):
        """Return the replacement for the name found."""
        return '(?P<%s>\\w+)' % name

    def lastly(self, regex):
        """Process the result of __call__ right before it returns."""
        return "^%s$" % regex

    def __call__(self, url_pattern):
        """Turn a url_pattern into regex."""
        parts = [part.split(self.end) 
                 for part in url_pattern.split(self.start)]
        parts = [y for x in parts for y in x]
        parts[::2] = map(re.escape, parts[::2])
        parts[1::2] = map(self.lookup, parts[1::2])
        return self.lastly(''.join(parts))


