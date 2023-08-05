import types

from rhubarbtart.threadobject import FakeObject
from rhubarbtart.httpobjects import Request, Response

from paste.request import parse_formvars
from paste.util import import_string
from paste import httpexceptions
from paste.deploy.converters import asbool
from paste import fileapp

__all__ = ['request', 'response', 'TartRootController', 'WSGIApp', 'expose',
           'make_middleware', 'httpobjects']

request = FakeObject('rhubarbtart.request')
response = FakeObject('rhubarbtart.response')

def expose(func):
    """
    Decorator to mark a method as public (having an ``.exposed``
    attribute indicates this; this decorator just sets that
    attribute).
    """
    func.exposed = True
    return func

def make_middleware(app, global_conf, **local_conf):
    """
    Wrap the basic application (typically based on TartRootController)
    in a standard set of middleware.
    """
    wrapped = app
    conf = global_conf.copy()
    conf.update(local_conf)
    debug = asbool(conf.get('debug', False))
    # First put into place httpexceptions, which must be most closely
    # wrapped around the application (it can interact poorly with
    # other middleware):
    if asbool(conf.get('use_httpexceptions', True)):
        wrapped = httpexceptions.make_middleware(
            wrapped, conf)
    if asbool(conf.get('use_recursive', True)):
        from paste import recursive
        wrapped = recursive.RecursiveMiddleware(
            wrapped, conf)
    if asbool(conf.get('use_session', True)):
        from paste import session
        wrapped = session.SessionMiddleware(
            wrapped, conf)
    if debug:
        if asbool(conf.get('use_wdg_validate', False)):
            from paste.debug import wdg_validate
            wrapped = wdg_validate.WDGValidateMiddleware(
                wrapped, conf)
        if asbool(conf.get('use_lint', False)):
            from paste import lint
            wrapped = lint.make_middleware(
                wrapped, conf)
        if asbool(conf.get('use_profile', False)):
            from paste.debug import profile
            wrapped = profile.ProfileMiddleware(
                wrapped, conf)
        if asbool(conf.get('use_interactive', False)):
            from paste import evalexception
            wrapped = evalexception.EvalException(
                wrapped, conf)
        else:
            from paste.exceptions import errormiddleware
            wrapped = errormiddleware.ErrorMiddleware(
                wrapped, conf)
        if asbool(conf.get('use_printdebug', True)):
            from paste.debug import prints
            wrapped = prints.PrintDebugMiddleware(
                wrapped, conf)
    from paste.deploy.config import ConfigMiddleware
    wrapped = ConfigMiddleware(wrapped, conf)
    return wrapped

class WSGIApp(object):
    """
    Used to wrap a WSGI application to put it in the object
    tree and have it invoked.

    Any object with a ``.wsgi_application`` attribute will do, this
    just happens to be an easy way to make such an attribute.

    Usage::

        class Root(object):
            foreign_app = WSGIApp(actual_wsgi_app)
    """

    exposed = True

    def __init__(self, app):
        self.wsgi_application = app

class TartRootController(object):

    root_object = None

    def __init__(self, root_object=None):
        if root_object is None:
            root_object = self
        if isinstance(root_object, basestring):
            root_object = import_string.eval_import(root_object)
        self.root_object = root_object

    def __call__(self, environ, start_response):
        req = Request(environ)
        res = Response()
        request._FAKE_attach(req)
        response._FAKE_attach(res)
        
        path = environ['PATH_INFO']
        path = path.strip('/')
        if not path:
            name_list = []
        else:
            name_list = path.split('/')
        used_names = []
        extra_names = name_list[:]
        name_list = name_list + ['index']
        if self.root_object is None:
            node = self
        else:
            node = self.root_object
        trail = []
        for name in name_list:
            objname = name.replace('.', '_')
            node = getattr(node, objname, None)
            if extra_names:
                # If not, probably the last 'index' entry
                used_names.append(extra_names.pop(0))
            if node == None:
                trail.append((name, node))
            else:
                trail.append((objname, node))

        handler = None
        # We keep track for a better 404 later:
        unexposed = None
        names = [name for name, candidate in trail]
        for i in xrange(len(trail) -1, -1, -1):
            name, candidate = trail[i]
            consumed_path = names[:i+1]
            positional_args = names[i+1:-1]

            defhandler = getattr(candidate, "default", None)
            if callable(defhandler) and getattr(defhandler, 'exposed', False):
                handler = defhandler
                break

            wsgihandler = None
            wsgi_application = getattr(candidate, "wsgi_application", None)
            if (wsgi_application
                and getattr(candidate, 'exposed', False)):
                if isinstance(wsgi_application, int):
                    wsgihandler = candidate
                else:
                    wsgihandler = wsgi_application

            if wsgihandler:
                # Should we reconstruct the current location for all
                # requests once we finish?  It's just as useful
                # to non-WSGI requests (maybe we should also just
                # put it in SCRIPT_NAME/PATH_INFO)
                script_name = '/' + '/'.join(consumed_path)
                path_info = '/' + '/'.join(positional_args)
                if path_info == '/' and not environ['PATH_INFO'].endswith('/'):
                    path_info = ''
                if path_info and script_name == '/':
                    script_name = ''
                environ['SCRIPT_NAME'] += script_name
                environ['PATH_INFO'] = path_info
                return wsgihandler(environ, start_response)

            # @@: I'm not sure what the purpose of callable is here?
            if callable(candidate):
                if getattr(candidate, 'exposed', False):
                    handler = candidate
                    break
                else:
                    unexposed = candidate

        if handler is None:
            if unexposed:
                comment = '%r not .exposed' % unexposed
            else:
                comment = None
            not_found = httpexceptions.HTTPNotFound(comment=comment)
            return not_found.wsgi_application(environ, start_response)

        formvars = parse_formvars(environ)
        if not formvars:
            formvars = {}
        res.body = handler(*positional_args, **formvars)

        # @@: Run Filters here

        return_value = convert_body(res.body)

        headers = res.headers.headeritems()
        start_response(res.status, headers)
        return return_value

def convert_body(value):
    # Convert the given value to an iterable object.
    if isinstance(value, types.FileType):
        value = fileapp._FileIter(value)
    elif isinstance(value, types.GeneratorType):
        value = flattener(value)
    elif isinstance(value, basestring):
        # strings get wrapped in a list because iterating over a single
        # item list is much faster than iterating over every character
        # in a long string.
        value = [value]
    elif value is None:
        value = []
    return value

def flattener(body):
    """Yield the given input, recursively iterating over each result
    (if needed)."""
    for x in body:
        if not isinstance(x, types.GeneratorType):
            yield x
        else:
            for y in flattener(x):
                yield y 
