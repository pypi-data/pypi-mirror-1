import sys
from inspect import getargspec
from clutch import ClutchError, config
from clutch.lib import ModelJSONEncoder, Request, Response, Bunch
from clutch.blob import SendBlobException
from webob.exc import HTTPNotFound
from django.utils import simplejson

import logging

log = logging.getLogger(__name__)

__all__ = ["BaseApp"]

class BaseApp(object):
    """Clutch's WSGI callable BaseApp"""

    def wsgi_init(self, environ, start_response):
        request = Request(environ)
        # assume UTF8 request encoding
        request.charset = 'utf8'
        request.kwargs = environ.get('wsgiorg.routing_args')[1]
        request.format =  request.kwargs.get('format', 'default')

        response = Response(environ, start_response)

        # add the context object
        environ['clutch.context'] = Bunch()
        return request, response

    def get_controller_class(self, controller):
        controller_parts = controller.split(".")
        controller_module = ".".join(controller_parts[:-1])
        controller_class_name = controller_parts[-1]

        try:
            __import__(controller_module)
        except ImportError, e:
            raise

        try:
            controller_class = getattr(sys.modules[controller_module], controller_class_name)
        except AttributeError, e:
            raise HTTPNotFound

        return controller_class

    def validate(self, controller, method):
        if not hasattr(method, '_validate'):
            return method
        for form_name, validator in method._validate.iteritems():
            handler = validator(controller)
            # We are going to assume that the error handler is
            # on the same controller as we need a method that is attached
            # to the controller handling the current request
            if not handler.__name__ == method.__name__:
                return getattr(controller, handler.__name__)
        return method

    def render(self, controller, method, result):
        if not hasattr(method, '_render'):
            if isinstance(result, (dict, list)):
                return simplejson.dumps(result, cls=ModelJSONEncoder)
            else:
                return result
        return method._render[controller.request.format](controller, result)

    def __call__(self, environ, start_response):
        try:
            url, match = environ['wsgiorg.routing_args']
        except KeyError, e:
            raise ClutchError('No URL routing info could be found (is Routes middleware installed?)')
        controller = match.get('controller')
        if not controller:
            raise HTTPNotFound

        controller_class = self.get_controller_class(controller)

        request, response = self.wsgi_init(environ, start_response)

        if not controller_class:
            raise ClutchError("Controller class '%s' not found" % controller)

        # create the controller and get the method to be executed
        controller = controller_class(request, response)
        action_method = getattr(controller, match['action'], None)
        if not action_method:
            raise HTTPNotFound
        action_method = self.validate(controller, action_method)

        # inject the forms
        if hasattr(action_method, '_forms'):
            controller.context.forms = action_method._forms
            # get the validated forms and override
            controller.context.forms.update(environ.get('clutch.validation', {}))

        # pass the args to the action_method for ease of use
        func_args = getargspec(action_method)[0][1:]
        kwargs = dict([i for i in request.kwargs.iteritems() if i[0] in func_args])

        try:
            result = action_method(**kwargs)
        except SendBlobException, e:
            return response()

        result = self.render(controller, action_method, result)

        if isinstance(result, basestring):
            response.body = result
        else:
            # assume an iterable
            response.app_iter = result

        return response()
