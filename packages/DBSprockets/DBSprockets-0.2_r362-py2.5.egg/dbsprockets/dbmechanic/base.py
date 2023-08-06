"""Provides the BaseController class for subclassing, and other objects
utilized by Controllers.
"""
from tg import TurboGearsController
from toscawidgets.api import WidgetBunch

class BaseController(TurboGearsController):
    
    def __call__(self, environ, start_response):
        """Invoke the Controller"""
        # TurboGearsController.__call__ dispatches to the Controller method
        # the request is routed to. This routing information is
        # available in environ['pylons.routes_dict']
        context.w = WidgetBunch()
        try:
            return TurboGearsController.__call__(self, environ, start_response)
        finally:
            self.Session.remove()

