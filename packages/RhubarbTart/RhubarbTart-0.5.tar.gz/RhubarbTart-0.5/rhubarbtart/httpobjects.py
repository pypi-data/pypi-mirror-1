"""Request and Response objects"""

from paste.request import parse_headers, parse_formvars, get_cookies
from paste import httpexceptions
from paste.response import HeaderDict

__all__ = ['Request', 'Response']

class environ_getter(object):
    """
    For delegating an attribute to a key in self.environ.
    """
    # @@: Also __set__?  Should setting be allowed?
    def __init__(self, key):
        self.key = key
    def __get__(self, obj, type=None):
        if type == None:
            return self
        return obj.environ.get(self.key, '')

class Request(object):
    """
    This object is instantiated in the threadlocal rhubarbtart.request variable
    upon every request to store various attributes about the current request:

    ``scheme``: This stores the scheme which the current URL was requested
    with.

    ``remote_addr``: The IP address of the host fetching the resource

    ``remote_post``: The remote port of the host fetching the resource

    ``remote_host``: The remote hostname of the host fetching the resource

    ``method``: The request method, for example, GET or POST

    ``app_path``: Where the application is currently mounted, used for creating
    absolute URLs

    ``protocol``: The protocol of the HTTP request, 1.0 or 1.1

    ``query_string``: The query string on the request

    ``object_path``: The path to the current function

    ``config``: The content of the Paste Deploy config section for this
    application

    ``headers``: A dictionary of headers from the request

    ``headers_list``: A list of tuples of headers from the request

    ``simple_cookie``: A SimpleCookie instance from the cookie headers

    ``path``: The full path to the currently location.

    ``environ``: The full WSGI environ
    """

    def __init__(self, environ):
        self.environ = environ

    scheme = environ_getter('wsgi.url_scheme')
    remoteAddr = remote_addr = environ_getter('REMOTE_ADDR')
    remotePort = remote_port = environ_getter('REMOTE_PORT')
    method = environ_getter('REQUEST_METHOD')
    app_path = environ_getter('SCRIPT_NAME')
    protocol = environ_getter('SERVER_PROTOCOL')
    query_string = queryString = environ_getter('QUERY_STRING')
    object_path = objectPath = environ_getter('PATH_INFO')
    # wsgi.input might need reseting or seeking or caching
    # or something to really be available:
    body = environ_getter('wsgi.input')
    config = environ_getter('paste.config')

    def remoteHost__get(self):
        import socket
        try:
            return socket.gethostbyname(self.environ['REMOTE_ADDR'])
        except socket.error:
            return self.environ['REMOTE_ADDR']
    remoteHost = remote_host = property(remoteHost__get)

    def headers__get(self):
        return HeaderDict(parse_headers(self.environ))
    headers = headerMap = property(headers__get)

    def header_list__get(self):
        return list(parse_headers(self.environ))
    headerList = header_list = property(header_list__get)

    def simpleCookie__get(self):
        return get_cookies(self.environ)
    simpleCookie = simple_cookie = property(simpleCookie__get)

    def base__get(self):
        return "://".join((self.scheme, self.environ['HTTP_HOST']))
    base = property(base__get)

    def params__get(self):
        return parse_formvars(self.environ)
    params = paramMap = property(params__get)
    def request_line__get(self):
        return ("%(REQUEST_METHOD)s %(SCRIPT_NAME)s%(PATH_INFO)s %(SERVER_PROTOCOL)s" 
                % self.environ)
    request_line = requestLine = property(request_line__get)
    def path__get(self):
        return ("%(SCRIPT_NAME)s%(PATH_INFO)s" % self.environ)
    path = property(path__get)

    def browser_url__get(self):
        return "".join((self.base,self.path))
    browser_url = browserUrl = property(browser_url__get)

class Response(object):
    """
    This object is instantiated in the threadlocal rhubarbtart.response variable
    upon every request to store various attributes about the current response:

    ``headers``: A dictionary of headers that can be changed

    ``status``: The status code to use for the response
    """

    def __init__(self):
        self._status = None
        self.status = '200 OK'
        self.headers = HeaderDict({'content-type': 'text/html'})

    def status__get(self):
        return self._status

    def status__set(self, value):
        if isinstance(value, int):
            value = str(value)
        if ' ' not in value:
            try:
                exc = httpexceptions.get_exception(int(value))
                value = value + ' ' + exc.title
            except KeyError:
                value = value + ' Unknown'
        self._status = value

    status = property(status__get, status__set)
