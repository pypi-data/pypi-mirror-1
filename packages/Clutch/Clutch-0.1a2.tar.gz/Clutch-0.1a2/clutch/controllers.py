import clutch
from clutch.lib import Bunch
from webob.exc import status_map

__all__ = ["ClutchController"]

class ClutchController(object):
    """
    Clutch's base controller class.
    """

    def __init__(self, request, response):
        self.request = request
        self.response = response

    @property
    def context(self):
        return self.request.environ['clutch.context']

    def url_for(self, *args, **kwargs):
        """A wrapper for routes.util.URLGenerator

        This wrapper simply takes the URLGenerator instance
        created by RoutesMiddleware from the context environ
        and passes through all args and kwargs."""
        return self.request.environ['routes.url'](*args, **kwargs)

    def redirect(self, location, code=302):
        """Raises a redirect depending on the code"""
        if code < 300 or code >= 400:
            raise clutch.ClutchError("Code $i is not a redirection" % code)

        exc = status_map[code]

        raise exc(location=location)

    def redirect_to(self, *args, **kwargs):
        """Uses url_for to redirect to a routes generated path"""
        # see if there's a code in kwargs
        code = kwargs.get('code', 302)
        if 'code' in kwargs:
            del kwargs['code']

        return self.redirect(self.url_for(*args, **kwargs), code)
