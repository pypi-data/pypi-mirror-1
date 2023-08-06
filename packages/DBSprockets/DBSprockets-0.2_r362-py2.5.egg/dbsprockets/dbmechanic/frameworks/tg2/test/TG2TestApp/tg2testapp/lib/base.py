"""Provides the BaseController class for subclassing, and other objects
utilized by Controllers.
"""
from pylons import c, cache, config, g, request, response, session
from tg import TurboGearsController, context
from pylons.controllers.util import abort, etag_cache, redirect_to
from pylons.decorators import jsonify
from pylons.i18n import _, ungettext, N_
from pylons.templating import render
from toscawidgets.api import WidgetBunch

import tg2testapp.model as model

class Controller(object):
    """Base class for a web application's controller.
    
    Currently, this provides positional parameters functionality
    via a standard default method.
    """
    
class BaseController(TurboGearsController):
    """Base class for the root of a web application.
    
    Your web application should have one of these. The root of
    your application is used to compute URLs used by your app.
    """
    
    def __call__(self, environ, start_response):
        """Invoke the Controller"""
        # TurboGearsController.__call__ dispatches to the Controller method
        # the request is routed to. This routing information is
        # available in environ['pylons.routes_dict']

        # Create a container to send widgets to the template. Only those sent
        # in here will have their resources automatically included in the
        # template
        context.w = WidgetBunch()
        try:
            return TurboGearsController.__call__(self, environ, start_response)
        finally:
            #after everything is done clear out the Database Session
            #so we don't have trouble with cross request DBSession
            #polution.
            model.DBSession.remove()
