from clutch import Bunch

__all__ = ["validate", "inject_form"]

def validate(form, error_handler, form_name='form'):
    def wrapper(method):
        def validate_form(controller):
            env_key = 'clutch.validation'
            form_obj = form(data=controller.request.POST)
            if not form_obj.is_valid():
                if not env_key in controller.environ:
                    controller.environ[env_key] = {}
                controller.environ[env_key][form_name] = form_obj
                return error_handler
            return method
        if not hasattr(method, '_validate'):
            setattr(method, '_validate', {})
        method._validate[form_name] = validate_form
        return method
    return wrapper

def inject_form(form, form_name='form'):
    def wrapper(method):
        if not hasattr(method, '_forms'):
            setattr(method, '_forms', Bunch())
        method._forms[form_name] = form
        return method
    return wrapper
