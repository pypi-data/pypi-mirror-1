"""Pylons middleware initialization"""
from paste.cascade import Cascade
from paste.registry import RegistryManager
from paste.urlparser import StaticURLParser
from paste.deploy.converters import asbool
from paste import httpexceptions

from pylons import config
from pylons.middleware import error_mapper, ErrorDocuments, ErrorHandler, \
    StaticJavascripts
from beaker.middleware import SessionMiddleware, CacheMiddleware
from tg import TurboGearsApplication
from toscawidgets.middleware import TGWidgetsMiddleware
from toscawidgets.mods.pylonshf import PylonsHostFramework


from  tg2testapp.config.environment import load_environment
from  tg2testapp.controllers.root import RootController

def make_app(global_conf, full_stack=True, **app_conf):
    """Create a Pylons WSGI application and return it

    ``global_conf``
        The inherited configuration for this application. Normally from
        the [DEFAULT] section of the Paste ini file.

    ``full_stack``
        Whether or not this application provides a full WSGI stack (by
        default, meaning it handles its own exceptions and errors).
        Disable full_stack when this application is "managed" by
        another WSGI middleware.

    ``app_conf``
        The application's local configuration. Normally specified in the
        [app:<name>] section of the Paste ini file (where <name>
        defaults to main).
    """
    # Configure the Pylons environment
    load_environment(global_conf, app_conf)
    
    # Create the TurboGears WSGI app stack
    app = TurboGearsApplication(RootController())
    
    # Add Session and Cashing support 
    app = SessionMiddleware(app, config)
    app = CacheMiddleware(app, config)
    
    # Configure and add ToscaWidgets support 
    host_framework = PylonsHostFramework(default_view="genshi")
    app = TGWidgetsMiddleware(app, host_framework)

    # CUSTOM MIDDLEWARE HERE (filtered by error handling middlewares)

    if asbool(full_stack):
        # Handle Python exceptions
        app = ErrorHandler(app, global_conf, **config['pylons.errorware'])

        # Display error documents for 401, 403, 404 status codes (and
        # 500 when debug is disabled)
        app = ErrorDocuments(app, global_conf, mapper=error_mapper, **app_conf)

    # Establish the Registry for this application
    app = RegistryManager(app)

    # Static files
    javascripts_app = StaticJavascripts()
    static_app = StaticURLParser(config['pylons.paths']['static_files'])
    app = Cascade([static_app, javascripts_app, app])
    return app
