from clutch import config, ClutchError
from clutch.lib import Bunch, ModelJSONEncoder
from django.utils import simplejson
from google.appengine.api import users
from google.appengine.ext import blobstore
import os

try:
    from mako.template import Template
except ImportError, e:
    Template = None

__all__ = ["mako", "plain", "json"]

def register_renderer(method, renderer, format, default):
    if not hasattr(method, '_render'):
        setattr(method, '_render', {})
    if default or not 'default' in method._render:
        method._render['default'] = renderer
    method._render[format] = renderer

def mako(template, format='html', content_type="text/html", charset='utf8', default=False):
    if Template is None:
        raise ClutchError("Mako is being used as a renderer and is not available for import")
    def wrapper(method):
        def render_mako(controller, result):
            resp = controller.response
            resp.charset = charset
            resp.content_type = content_type
            context = controller.request.environ['clutch.context']

            if not isinstance(result, dict):
                raise TypeError("Mako renderer requires a result of type 'dict', not '%s'" % type(result))

            if not 'g' in result:
                result['g'] = Bunch(request=controller.request,
                                    context=context,
                                    url_for=controller.url_for,
                                    user=users.get_current_user(),
                                    user_is_admin=users.is_current_user_admin(),
                                    users=users,
                                    create_upload_url=blobstore.create_upload_url,
                                   )

            template_path = config.dotted_filename_finder.get_dotted_filename(template)
            if not os.path.exists(template_path):
                raise ClutchError("Mako template at '%s' could not be found" % template_path)

            return Template(filename=template_path, lookup=config.template_lookup).render(**result)

        register_renderer(method, render_mako, format, default)
        # We return the original method here
        return method
    return wrapper

def plain(format='txt', content_type="text/plain", charset='utf8', default=False):
    def wrapper(method):
        def render_plain(controller, result):
            resp = controller.response
            resp.content_type = content_type
            resp.charset = charset
            return str(result)
        register_renderer(method, render_mako, format, default)
        return method
    return wrapper

def json(format='json', content_type="application/json", charset='utf8', default=False):
    def wrapper(method):
        def render_json(controller, result):
            resp = controller.response
            resp.content_type = content_type
            resp.charset = charset
            return simplejson.dumps(result, cls=ModelJSONEncoder)
        register_renderer(method, render_json, format, default)
        return method
    return wrapper

