from decorator import decorator

#from toscawidgets.api import retrieve_resources
#from toscawidgets.mods.base import HostFramework
#from toscawidgets.view import EngineManager

import pylons
from pylons.util import AttribSafeContextObj, ContextObj
from pylons.i18n import ugettext
from pylons.templating import render

from formencode import Invalid

def validate(form=None, validators=None, error_handler=None, post_only=True, 
             state_factory=None):
    """Validate input using a ToscaWidgetsForms form.
    
    Given a TW form or dict of validators, validate will attempt to validate
    the form or validator list as long as a POST request is made. No 
    validation is performed on GET requests.
    
    If validation was succesfull, the valid result dict will be saved
    as ``self.form_result``. Otherwise, the action will be re-run as if it was a
    GET, and the form will redisplay errors and previous input values.
    form field errors.
    
    If you'd like validate to also check GET (query) variables during its 
    validation, set the ``post_only`` keyword argument to False.
    
    """
    def wrapper(func, self, *args, **kwargs):
        """Decorator Wrapper function"""
        if not pylons.request.method == 'POST':
            return func(self, *args, **kwargs)
        if post_only:
            params = pylons.request.POST.copy()
        else:
            params = pylons.request.params.copy()
            
        errors = {}

        state = None
        if state_factory:
            state = state_factory()
        
        sprocket = self.sprockets[params['dbsprockets_id']]
        form = sprocket.view.widget
        if form:
            try:
                self.form_result = form.validate(params, state=state)
            except Invalid, e:
                self.validation_exception = e
                errors = True

        if validators:
            if isinstance(validators, dict):
                if not hasattr(self, 'form_result'):
                    self.form_result = {}
                for field, validator in validators.iteritems():
                    try:
                        self.form_result[field] = \
                            validator.to_python(decoded[field] or None, state)
                    except Invalid, error:
                        errors[field] = error

        if errors:
            self.errors = errors
            pylons.request.environ['REQUEST_METHOD'] = 'GET'
            if error_handler:
                pylons.request.environ['pylons.routes_dict'] = error_handler
            return self._perform_call(None, dict(url=error_handler))
        return func(self, *args, **kwargs)
    return decorator(wrapper)

def crudErrorCatcher(errorType=None, error_handler=None):
    def wrapper(func, self, *args, **kwargs):
        """Decorator Wrapper function"""
        try:
            value = func(self, *args, **kwargs)
        except errorType, e:
            
            pylons.request.environ['pylons.routes_dict'] = error_handler
            return self._perform_call(None, dict(url=error_handler))
        return value
    return decorator(wrapper)
