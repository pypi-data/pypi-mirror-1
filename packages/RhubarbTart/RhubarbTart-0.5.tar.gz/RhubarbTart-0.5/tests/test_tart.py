from paste.fixture import TestApp
from paste.request import parse_formvars
from rhubarbtart import TartRootController, WSGIApp,expose

class Root(TartRootController):
    def __init__(self):
        self.nested2 = Nested2()
        self.name = DefaultTest()
    def index(self):
        return "Hello World!"
    index.exposed = True

    def show_message(self):
        return "Hello World!"
    expose(show_message)
    def greet_message(self, name = None):
        if name:
            return name
        else:
            return "No Name"
    greet_message.exposed = True
    def yielding(self):
        yield "Hello World"
        yield "Hello World Again"
    expose(yielding)

    def nested_yielding(self):
        def inner_yield():
            yield "Hello World"
        yield inner_yield()
    expose(nested_yielding)

    def do_not_find(self):
        print "Never get here"

class Nested1(object):
    def index(self):
        return "Nested1"
    index.exposed = True

class Nested2(object):
    def index(self):
        return "Nested2"
    index.exposed = True

class DefaultTest(object):
    def default(self, name):
        return name
    default.exposed = True


def simple_wsgi_app(environ, start_response):
    start_response('200 OK', [('content-type', 'text/plain')])
    return ['%(SCRIPT_NAME)s:%(PATH_INFO)s' % environ]

simple_wsgi_app.wsgi_application = True

wsgi_app = Root()
wsgi_app.nested1 = Nested1()
wsgi_app.nest_wsgi = WSGIApp(simple_wsgi_app)
wsgi_app.nest_wsgi2 = simple_wsgi_app
wsgi_app.nest_wsgi2.wsgi_application = True
wsgi_app.nest_wsgi2.exposed = True
test_app = TestApp(wsgi_app)

def test_index():
    res = test_app.get('/')
    assert 'Hello World!' in res

def test_simple_function_resolve():
    res = test_app.get('/show_message')
    assert 'Hello World!' in res

def test_simple_get():
    res = test_app.get('/greet_message', dict(name="name"))
    assert 'name' in res

def test_not_found():
    res = test_app.get('/not_found', status=404)

def test_nested1():
    res = test_app.get('/nested1')
    assert 'Nested1' in res

def test_nested2():
    res = test_app.get('/nested2')
    assert 'Nested2' in res

def test_wsgi():
    res = test_app.get('/nest_wsgi/')
    assert res.body == '/nest_wsgi:/'
    res = test_app.get('/nest_wsgi')
    assert res.body == '/nest_wsgi:'
    res = test_app.get('/nest_wsgi/foo/bar')
    assert res.body == '/nest_wsgi:/foo/bar'

def test_wsgi2():
    res = test_app.get('/nest_wsgi2/')
    assert res.body == '/nest_wsgi2:/'
    res = test_app.get('/nest_wsgi2')
    assert res.body == '/nest_wsgi2:'
    res = test_app.get('/nest_wsgi2/foo/bar')
    assert res.body == '/nest_wsgi2:/foo/bar'

def test_default():
    res = test_app.get('/name/name')
    assert 'name' in res

def test_yielding():
    res = test_app.get('/yielding')
    assert 'Hello World Again' in res

def test_nested_yielding():
    res = test_app.get('/nested_yielding')
    assert 'Hello World' in res

def test_do_not_find():
    res = test_app.get('/do_not_find', status=404)
    print res
    assert 'Not Found' in res
