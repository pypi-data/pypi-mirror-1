from paste.util.threadinglocal import local

def dispatcher(method):
    def replacement(self, *args, **kw):
        return getattr(self._FAKE_getobj(method), method)(*args, **kw)
    return replacement

class FakeObject(object):

    def __init__(self, description):
        self.__dict__['_FAKE_dispatcher'] = local()
        self.__dict__['_FAKE_description'] = description

    def _FAKE_getobj(self, attr=None):
        if not hasattr(self._FAKE_dispatcher, 'object'):
            if attr:
                raise AttributeError(
                    "Cannot access .%s: _FAKE_attach on object %s has not "
                    "been called yet to attach a root object" %
                    (attr, self._FAKE_description))
            else:
                raise AttributeError(
                    "_FAKE_attach on object %s has not been called yet to "
                    "attach a root object" % self._FAKE_description)
        return self._FAKE_dispatcher.object

    def __getattr__(self, attr):
        if attr.startswith('__'):
            raise AttributeError
        return getattr(self._FAKE_getobj(attr), attr)

    def __setattr__(self, attr, value):
        setattr(self._FAKE_getobj(), attr, value)

    def _FAKE_attach(self, object):
        assert object is not self, (
            "Attempting to attach a threadlocal object to itself!")
        self._FAKE_dispatcher.object = object

    def _FAKE_detach(self, ignore_missing=False):
        if not hasattr(self._FAKE_dispatcher, 'object'):
            if ignore_missing:
                return
            raise AttributeError(
                "You cannot detach the root object when no object "
                "has been attached yet")
        del self._FAKE_dispatcher.object

    def __nonzero__(self):
        # We can't dispatch this method, because the object may
        # be truish or falsish without actually implementing this
        # exact method (e.g., it can implement __len__)
        return bool(self._FAKE_dispatcher.object)

for attr in ['__getitem__', '__setitem__', '__delitem__',
             '__contains__', '__iter__',
             '__len__', 'get', '__str__', '__add__']:
    setattr(FakeObject, attr, dispatcher(attr))

class FakeString(FakeObject):

    def __radd__(self, other):
        if isinstance(other, (str, unicode, self.__class__)):
            return str(other) + str(self)
        else:
            raise TypeError(
                "I don't know how to add a %r to a string"
                % other)
