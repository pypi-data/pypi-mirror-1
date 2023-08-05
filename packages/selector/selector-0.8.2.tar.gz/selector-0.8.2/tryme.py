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
from selector import Selector, status_app, \
                     EnvironDispatcher, MiddlewareComposer

t = Template("Hello $name, \n\tWelcome to the selector.")

def say_hello(environ, start_response):
    """Say hello based on the name in a path like /hello/(name)"""
    start_response("200 OK", [('Content-type', 'text/plain')])
    return [t.safe_substitute(environ['selector.vars'])]


def var_equ(val):
    def fn(env):
        if env['selector.vars']['val'] == val:
            return True
    return fn

erules = [(var_equ('one'), status_app('200 Ok', 'hello one')),
          (var_equ('two'), status_app('200 Ok', 'hello two')),
          (lambda x: True, status_app('200 Ok', 'hello blarg'))]

envdis = EnvironDispatcher(erules)

def middle_say(word):
    def m(fn):
        def a(env, sr):
            ret = list(fn(env, sr))
            ret.insert(0, word+'(')
            ret.append(')')
            return ret
        return a
    return m

mrules = [(var_equ('one'), middle_say("one")),
          (var_equ('two'), middle_say("two")),
          (lambda x: True, middle_say("always"))]

app = status_app('200 Ok', 'app-to-wrap')

composer = MiddlewareComposer(app, mrules)

structure = [(r'/foo[/]?$', {'GET': status_app('200 OK', 'hello foo')}),
             (r'/bar[/]?$', {'GET': status_app('200 OK', 'hello bar')}),
             (r'/baz[/]?$', {'GET': status_app('200 OK', 'hello baz')})]

structure2 = [('/yo[/[{name}[/]]]', {'GET': say_hello}),
              ('/envdis/{val}[/]', {'GET': envdis}),
              ('/compose/{val}[/]', {'GET': composer}),
              ('/whatup/{name:number}[/]', {'GET': say_hello})]

s = Selector(structure2, prefix='/fluptest')
s.slurp(structure, prefix='^/fluptest', parser=lambda x: x)
s.add('/hello/{name}', GET=say_hello)

s.slurp_file('test.map')

if __name__ == '__main__':
    """Run the app with the Selector with the flup SCGI server."""
    from flup.server.scgi import WSGIServer
    WSGIServer(s).run()

