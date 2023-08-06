from clutch import dottedtemplatelookup
from clutch.lib import Bunch

__all__ = ["ClutchError", "config", "update_config"]

class ClutchError(Exception):
    """This exception is raised whenever there is a problem
    doing anything with the framework"""

config = Bunch() # This should be extended when the app is started in main.py
config.dotted_filename_finder = dottedtemplatelookup.DottedFilenameFinder()
config.template_lookup = dottedtemplatelookup.DottedTemplateLookup(input_encoding='utf-8',
                                                                   output_encoding='utf-8',
                                                                   imports=[],
                                                                   default_filters=[])

def update_config(conf_module):
    mod_attrs = dir(conf_module)
    for attr_name in mod_attrs:
        attr = getattr(conf_module, attr_name)
        # only update the config if the attr is a Bunch or dict
        if isinstance(attr, (Bunch, dict)):
            # Check to see if we already have this config obj
            if hasattr(config, attr_name):
                getattr(config, attr_name).update(attr)
            else:
                setattr(config, attr_name, attr)
