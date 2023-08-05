"""tryme - try out selector with flup's scgi server

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
from string import Template
from selector import Selector, status_app

t = Template("Hello $name, \n\tWelcome to the selector.")

def say_hello(environ, start_response):
    """Say hello based on the name in a path like /hello/(name)"""
    start_response("200 OK", [('Content-type', 'text/plain')])
    return [t.safe_substitute(environ['selector.vars'])]


structure = [(r'/foo[/]?$', {'GET': status_app('200 OK', 'hello foo')}),
             (r'/bar[/]?$', {'GET': status_app('200 OK', 'hello bar')}),
             (r'/baz[/]?$', {'GET': status_app('200 OK', 'hello baz')})]

s = Selector(structure, prefix="^/fluptest")
# s.slurp(structure)
s.add(r'/hello/(?P<name>[a-zA-Z]+)$', {'GET': say_hello})

if __name__ == '__main__':
    """Run the app with the Selector with the flup SCGI server."""
    from flup.server.scgi import WSGIServer
    WSGIServer(s).run()

