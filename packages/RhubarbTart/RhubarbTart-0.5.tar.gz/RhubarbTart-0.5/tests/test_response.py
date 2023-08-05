from paste.fixture import TestApp
from paste.request import parse_formvars
from rhubarbtart import TartRootController, response

class Response(TartRootController):
    def index(self):
        response.status = 404
        response.headers['Content-type'] = 'text/xml'
        return 'XML Not Found Message'
    index.exposed = True

    def unknown_returncode(self):
        response.status = 420
        return 'Unknown return code'
    unknown_returncode.exposed = True

wsgi_app = Response()
test_app = TestApp(wsgi_app)

def test_index():
    res = test_app.get('/', status=404)
    assert res.header('Content-type') == 'text/xml'
    assert 'XML Not Found Message' in res

def test_unknown_returncode():
    res = test_app.get('/unknown_returncode', status=420)
    assert 'Unknown return code' in res
