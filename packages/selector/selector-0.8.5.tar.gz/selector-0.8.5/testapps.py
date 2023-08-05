
class FooApp(object):
    def __init__(self, test_string):
        self.test_string = test_string
    def __call__(self, environ, start_response):
        id = environ['selector.vars'].get('id', 'default')
        start_response("200 Ok", [('Content-type', 'text/plain')])
        return ["The id was %s\nThe test string was %s" 
                % (id, self.test_string)]

