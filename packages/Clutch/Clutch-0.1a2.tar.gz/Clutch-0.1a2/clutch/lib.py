from django.utils import simplejson
from google.appengine.ext import db
from google.appengine.api import users
from webob import Request, Response as WebObResponse

__all__ = ['ModelJSONEncoder', 'Request', 'Response', 'EnvironProxy', 'ProxyError',
           'bind_environ', 'Bunch']

class ModelJSONEncoder(simplejson.JSONEncoder):
    """
    JSONEncoder subclass that knows how to encode db.Model objects
    """

    def default(self, o):
        if callable(getattr(o, '__json__', None)):
            return o.__json__()
        elif issubclass(o.__class__, db.Model):
            model_data = dict(key=str(o.key()), kind=o.kind())
            for field_name in o.fields().keys():
                model_data[field_name] = getattr(o, field_name)
            return model_data
        elif isinstance(o, users.User):
            user_data = dict(email=o.email)
        else:
            return super(ModelJSONEncoder, self).default(o)

class Response(WebObResponse):
    """A slightly more friendly response object."""
    def __init__(self, environ, start_request, **kw):
        super(Response, self).__init__(**kw)
        self.environ = environ
        self.start_request = start_request

    def __call__(self):
        return super(Response, self).__call__(self.environ, self.start_request)

    def error(self, status, e):
        self.status = status
        self.body = str(e)
        self.content_type = 'text/plain'

class Bunch(dict):
    """A dict like object with the ability to get/set
    data via attribute access.

    >>> data = Bunch(foo='bar', baz=1)
    >>> data.foo
    'bar'
    >>> data['foo']
    'bar'
    >>> data.baz
    1
    >>> data['baz']
    1
    """
    def __getattr__(self, attr):
        try:
            return self[attr]
        except KeyError:
            raise AttributeError("%s not found" % attr)

    def __setattr__(self, attr, value):
        self[attr] = value

class ProxyError(Exception):
    """Raised when there is a problem accessing the environ
    using an EnvironProxy instance"""

def bind_environ(proxy, environ):
    proxy.__dict__['____environ__'] = environ

class EnvironProxy(object):
    """Inspired by paste.registry"""
    def __init__(self, name):
        self.__dict__['____name__'] = name

    def __getattr__(self, attr):
        return getattr(self._proxied_obj(), attr)

    def __setattr__(self, attr, value):
        setattr(self._proxied_obj(), attr, value)

    def __delattr__(self, attr):
        delattr(self._proxied_obj(), attr)

    def __getitem__(self, key):
        return self._proxied_obj()[key]

    def __setitem__(self, key, value):
        self._proxied_obj()[key] = value

    def __delitem__(self, key):
        del self._proxied_obj()[key]

    def __call__(self, *args, **kw):
        return self._proxied_obj()(*args, **kw)

    def __iter__(self):
        return iter(self._proxied_obj())

    def __len__(self):
        return len(self._proxied_obj())

    def __contains__(self, key):
        return key in self._proxied_obj()

    def __nonzero__(self):
        return bool(self._proxied_obj())

    def _proxied_obj(self):
        try:
            environ = self.__dict__['____environ__']
            return environ[self.__dict__['____name__']]
        except (AttributeError, KeyError):
            raise ProxyError


