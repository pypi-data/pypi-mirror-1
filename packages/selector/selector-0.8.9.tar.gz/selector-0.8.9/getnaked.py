
from selector import Naked, expose, ByMethod


class ByMethodTest(ByMethod):

    def GET(self, environ, start_response):
        start_response("200 OK", [('Content-type', 'text/html')])
        return ["""<html><head><title>Test</title></head>
        <body>
            <form method="POST" action=""><input type="submit"/></form>
        </body></html>"""]

    def PUT(self, environ, start_response):
        start_response("200 OK", [('Content-type', 'text/plain')])
        return ["post modern"]
 

class Hellos(Naked):

    def luke(self, environ, start_response):
        start_response("200 OK", [('Content-type', 'text/plain')])
        return ["hello luke!"]
        
    def jess(self, environ, start_response):
        start_response("200 OK", [('Content-type', 'text/plain')])
        return ["hello jess!"]


class MyTest(Naked):

    _expose_all = False
    
    hello = expose(Hellos())

    bye = Hellos()

    bymeth = expose(ByMethodTest())

    def priv_hello(self, environ, start_response):
        start_response("200 OK", [('Content-type', 'text/plain')])
        return ["private here!"]


if __name__ == '__main__':
    """Run the app with the Selector with wsgiref."""
    from wsgiref.simple_server import make_server
    try:
        make_server('localhost', 9999, MyTest()).serve_forever()
    except KeyboardInterrupt, ki:
        print 'Thanks for playing!'
