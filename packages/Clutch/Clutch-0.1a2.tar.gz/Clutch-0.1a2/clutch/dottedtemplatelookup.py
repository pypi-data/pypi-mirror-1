"""a reimplementation of the mako template loader
which supports dotted names.

Adapted from tg2 dottednamesupport.py"""

import os
import stat
import clutch
from mako.template import Template
import threading

__all__ = ["DottedFilenameFinder", "DottedTemplateLookup"]

def resource_filename(package, filename):
    """This is a simple implementation of pkg_resources.resource_filename
    for use in App Engine as it doesn't seem to like pkg_resources much"""
    # import package
    mod = __import__(package, globals(), locals(), [''])
    # find package __file__
    path = mod.__file__
    # remove the last part of the path as it should be a .py
    path = "/".join(path.split("/")[:-1])

    return "%s/%s" % (path, filename)

class DottedFilenameFinder(object):
    """this class implements a cache system above the
    get_dotted_filename function and is designed to be
    created as `clutch.context.dotted_filename_finder`.
    """
    def __init__(self):
        self.__cache = dict()

    def get_dotted_filename(self, template_name, template_extension='.mako'):
        """this helper function is designed to search a template or any other
        file by python module name.

        Given a string containing the file/template name passed to the @expose
        decorator we will return a resource useable as a filename even
        if the file is in fact inside a zipped egg.

        @param template_name: the string representation of the template name
        as it has been given by the user on his @expose decorator.
        Basically this will be a string in the form of:
        "myapp.templates.somename"
        @type template_name: string

        @param template_extension: the extension we excpect the template to have,
        this MUST be the full extension as returned by the os.path.splitext
        function. This means it should contain the dot. ie: '.html'

        This argument is optional and the default value if nothing is provided will
        be '.mako'
        @type template_extension: string
        """
        try:
            return self.__cache[template_name]
        except KeyError:
            # the template name was not found in our cache
            divider = template_name.rfind('.')
            if divider >= 0:
                package = template_name[:divider]
                basename = template_name[divider + 1:] + template_extension
                try:
                    result = resource_filename(package, basename)
                except ImportError, e:
                    raise clutch.ClutchError(e.message +". Perhaps you have forgotten an __init__.py in that folder.")
            else:
                result = template_name

            self.__cache[template_name] = result

            return result

class DottedTemplateLookup(object):
    """Mako template lookup emulation that supports
    zipped applications and dotted filenames.

    This is an emulation of the Mako template lookup that will handle
    get_template and support dotted names in Python path notation
    to support zipped eggs.

    This is necessary because Mako asserts that your project will always
    be installed in a zip-unsafe manner with all files somewhere on the
    hard drive.

    This is not the case when you want your application to be deployed
    in a single zip file (zip-safe). If you want to deploy in a zip
    file _and_ use the dotted template name notation then this class
    is necessary because it emulates files on the filesystem for the
    underlying Mako engine while they are in fact in your zip file.
    """

    def __init__(self, input_encoding, output_encoding,
            imports, default_filters):

        self.input_encoding = input_encoding
        self.output_encoding = output_encoding
        self.imports = imports
        self.default_filters = default_filters
        # implement a cache for the loaded templates
        self.template_cache = dict()
        # implement a cache for the filename lookups
        self.template_filenames_cache = dict()

        # a mutex to ensure thread safeness during template loading
        self._mutex = threading.Lock()

    def adjust_uri(self, uri, relativeto):
        """Adjust the given uri relative to a filename.

        This method is used by mako for filesystem based reasons.
        In dotted lookup land we don't adjust uri so we just return
        the value we are given without any change.

        """
        if '.' in uri:
            # We are in the DottedTemplateLookup system so dots in
            # names should be treated as a Python path. Since this
            # method is called by template inheritance we must
            # support dotted names also in the inheritance.
            finder = clutch.config.dotted_filename_finder

            result = finder.get_dotted_filename(
                            template_name=uri,
                            template_extension='.mako')

            if not self.template_filenames_cache.has_key(uri):
                # feed our filename cache if needed.
                self.template_filenames_cache[uri] = result

        else:
            # no dot detected, just return plain name
            result = uri

        return result

    def __check(self, template):
        """private method used to verify if a template has changed
        since the last time it has been put in cache...

        This method being based on the mtime of a real file this should
        never be called on a zipped deployed application.

        This method is a ~copy/paste of the original caching system from
        the Mako lookup loader.

        """
        if template.filename is None:
            return template

        if not os.path.exists(template.filename):
            # remove from cache.
            self.template_cache.pop(template.filename, None)
            raise exceptions.TemplateLookupException(
                    "Cant locate template '%s'" % template.filename)

        elif template.module._modified_time < os.stat(
                template.filename)[stat.ST_MTIME]:

            # cache is too old, remove old template
            # from cache and reload.
            self.template_cache.pop(template.filename, None)
            return self.__load(template.filename)

        else:
            # cache is correct, use it.
            return template

    def __load(self, filename):
        """real loader function. copy paste from the mako template
        loader.

        """
        # make sure the template loading from filesystem is only done
        # one thread at a time to avoid bad clashes...
        self._mutex.acquire()
        try:
            try:
                # try returning from cache one more time in case
                # concurrent thread already loaded
                return self.template_cache[filename]

            except KeyError:
                # not in cache yet... we can continue normally
                pass

            try:
                self.template_cache[filename] = Template(open(filename).read(),
                    filename=filename,
                    input_encoding=self.input_encoding,
                    output_encoding=self.output_encoding,
                    default_filters=self.default_filters,
                    imports=self.imports,
                    lookup=self)

                return self.template_cache[filename]

            except:
                self.template_cache.pop(filename, None)
                raise

        finally:
            # _always_ release the lock once done to avoid
            # "thread lock" effect
            self._mutex.release()

    def get_template(self, template_name):
        """this is the emulated method that must return a template
        instance based on a given template name
        """

        if not self.template_cache.has_key(template_name):
            # the template string is not yet loaded into the cache.
            # Do so now
            self.__load(template_name)

        #TODO: use the paste asbool function here.
        #if asbool(tg.config.get('templating.mako.reloadfromdisk', 'false')):
            # AUTO RELOADING will be activated only if user has
            # explicitly asked for it in the configuration
            # return the template, but first make sure it's not outdated
            # and if outdated, refresh the cache.
        #    return self.__check(self.template_cache[template_name])

        #else:
        return self.template_cache[template_name]
