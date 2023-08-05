from paste.fixture import TestApp
from paste.request import parse_formvars
from rhubarbtart import TartRootController, WSGIApp, request

#This object contains one URL for each attribute in request
class Request(TartRootController):
    """Each function in is designed to test the request variable it has the
    same name as"""

    def index(self):
        return "Hello World"
    index.exposed = True

    def scheme(self):
        return request.scheme
    scheme.exposed = True

    def remote_addr(self):
        return request.remote_addr
    remote_addr.exposed = True

    def remote_port(self):
        return request.remote_port
    remote_port.exposed = True

    def remote_host(self):
        return str(request.remote_host)
    remote_host.exposed = True
    def headers(self):
        output = []
        for header, value in request.headers.iteritems():
            output.append(": ".join((header, str(value))))
        return "\n".join(output)
    headers.exposed = True

    def header_list(self):
        output = []
        for header in request.header_list:
            output.append(": ".join(header))
        return "\n".join(output)
    header_list.exposed = True

    def request_line(self):
        return request.request_line
    request_line.exposed = True

    def simple_cookie(self):
        return str(request.simple_cookie)
    simple_cookie.exposed = True

#@@: Still need to figure out file upload

    def method(self):
        return request.method
    method.exposed = True

    def protocol(self):
        return request.protocol
    protocol.exposed = True

    def query_string(self, test=None):
        return request.query_string
    query_string.exposed = True

    def path(self):
        return request.path
    path.exposed = True

    def params(self, *args, **kwargs):
        output = []
        for param, value in request.params.iteritems():
            output.append(": ".join((param, str(value))))
        return "\n".join(output)
    params.exposed = True

    def base(self):
        return request.base
    base.exposed = True

    def browser_url(self):
        return request.browser_url
    browser_url.exposed = True
    def object_path(self):
        return request.object_path
    object_path.exposed = True

wsgi_app = Request()
test_app = TestApp(wsgi_app)

def test_index():
    res = test_app.get('/')
    assert 'Hello World' in res

def test_scheme():
    res = test_app.get('/scheme')
    assert 'http' in res
    res = test_app.get('/scheme', extra_environ={'wsgi.url_scheme': 'https'})
    assert 'https' in res

def test_remote_addr():
    res = test_app.get('/remote_addr', extra_environ={'REMOTE_ADDR': '127.0.0.1'})
    assert '127.0.0.1' in res

def test_remote_port():
    res = test_app.get('/remote_port', extra_environ={'REMOTE_PORT': '12345'})
    assert '12345' in res

def test_remote_host():
    res = test_app.get('/remote_host', extra_environ={'REMOTE_ADDR': 'localhost'})
    assert '127.0.0.1' in res

def test_headers():
    res = test_app.get('/headers', headers={'X-Test-Header': 'Testing'})
    assert 'X-Test-Header: Testing' in res

def test_header_list():
    res = test_app.get('/header_list', headers={'X-Test-Header': 'Testing'})
    assert 'X-Test-Header: Testing' in res

def test_request_line():
    res = test_app.get('/request_line')
    assert 'GET /request_line HTTP/1.0' in res
    res = test_app.get('/request_line', extra_environ={'SCRIPT_NAME': '/test'})
    assert 'GET /test/request_line HTTP/1.0' in res

def test_simple_cookie():
    res = test_app.get('/simple_cookie', headers={'Cookie': 'cookie=wantcookie'})
    assert 'cookie=wantcookie' in res

#@@: Still need to figure out file upload

def test_method():
    res = test_app.get('/method')
    assert 'GET' in res
    res = test_app.post('/method')
    assert 'POST' in res

def test_protocol():
    res = test_app.get('/protocol')
    assert 'HTTP/1.0' in res

def test_query_string():
    res = test_app.get('/query_string?test=test')
    assert 'test=test' in res

def test_path():
    res = test_app.get('/path')
    assert '/path' in res
    res = test_app.get('/path', extra_environ={'SCRIPT_NAME': '/test'})
    assert '/test/path' in res

def test_params():
    res = test_app.get('/params', dict(test='test'))
    assert 'test: test' in res

def test_base():
    res = test_app.get('/base')
    assert 'http://localhost' in res

def test_browser_url():
    res = test_app.get('/browser_url')
    assert 'http://localhost/browser_url' in res

def test_object_path():
    res = test_app.get('/object_path')
    assert '/object_path' in res
