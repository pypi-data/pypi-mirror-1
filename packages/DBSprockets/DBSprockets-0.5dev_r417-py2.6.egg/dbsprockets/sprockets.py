"""
Sprockets Module

This is sort of like the central nervous system of dbsprockets.  Views and
Sessions are collected in separate caches and served up as sprockets.
The cache objects may be solidified at some point with a parent class.
They work for right now.


Classes:
Name           Description
Sprockets      A cache of Sprockets
Sprocket       A binding of Session and View configs
Views          A cache of Views
Sessions       A cache of Sessions

Exceptions:
SessionConfigError
ViewConfigError

Functions:
None

Copywrite (c) 2007 Christopher Perkins
Original Version by Christopher Perkins 2007
Released under MIT license.
"""
import types

from dbsprockets.viewfactory import ViewFactory
from dbsprockets.viewconfig import *
from dbsprockets.sessionconfig import *
from dbsprockets.saprovider import SAProvider
from dbsprockets.iprovider import IProvider
from dbsprockets.metadata import *
from dbsprockets.view import View

class SessionConfigError(Exception):pass
class ViewConfigError(Exception):pass

class Views(dict):
    """Container for View Objects"""
    def __init__(self, provider, controller):
        """Construct a Views Object.  This object is capable of creating ViewConfigs and
        acting as a widget cache for the views once they have been created from the ViewConfigs.
        Future implementations will have the ability to register different ViewConfig defaults.

        provider
            a ``IProvider`` object to instantiate views with.  Usually this is an SAProvider

        controller
            String.  This is a link to the URL in the application where the view is intended to
            be mounted.  I am hoping this is eliminated in the future.
        """

        if not isinstance(provider, IProvider):
            raise TypeError('provider is not of type IProvider')
        if not isinstance(controller, types.StringTypes):
            raise TypeError('controller is not of type String')
        self.view_factory = ViewFactory()
        self.provider = provider
        self.controller = controller

    default_view_configs = {'database_view': DatabaseViewConfig,
                          'edit_record'  : EditRecordViewConfig,
                          'add_record'   : AddRecordViewConfig,
                          'table_view'   : TableViewConfig,
                          'table_def'    : TableDefViewConfig,
                          }

    separator = '__'
    def _get_view(self, key):
        if self.separator not in key:
            identifier = ''
            view_type = key
        else:
            view_type, identifier = key.split(self.separator)
        if view_type not in self.default_view_configs:
            raise ViewConfigError('view_type:%s not found in default Views'%view_type)
        view_config = self.default_view_configs[view_type](self.provider, identifier, self.controller)
        self[key] = self.view_factory.create(view_config, id=key)
        return self[key]

    def __getitem__(self, key):
        if dict.__contains__(self, key):
            return dict.__getitem__(self, key)
        view = self._get_view(key)
        self[key] = view
        return view

    def __setitem__(self, key, item):
        if not isinstance(item, View):
            raise TypeError('item must be of type View')
        return dict.__setitem__(self, key, item)

class Sessions(dict):
    """Container for SessionConfigs"""

    def __init__(self, provider):
        """Construct a Sessions Object.  This object is capable of creating SessionConfigs and storing them
        based on the database schema objects they get data from.  It acts as a cache so that objects need-not
        be recreated every time a request is made for a widget.

        provider
            a ``IProvider`` object to instantiate views with.  Usually this is an SAProvider
        """
        if not isinstance(provider, IProvider):
            raise TypeError('provider is not of type IProvider')
        self.provider = provider

    default_session_configs = { 'database_view': DatabaseSessionConfig,
                              'table_def'    : SessionConfig,
                              'view_record'  : SessionConfig,
                              'table_view'   : TableViewSessionConfig,
                              'edit_record'  : EditRecordSessionConfig,
                              'add_record'   : AddRecordSessionConfig,
                             }

    def __getitem__(self, key):
        if dict.__contains__(self, key):
            return dict.__getitem__(self, key)
        session = self._get_session(key)
        self[key] = session
        return session

    separator = '__'
    def _get_session(self, key):
        if self.separator not in key:
            identifier = ''
            viewType = key
        else:
            viewType, identifier = key.split(self.separator)
        if viewType in self.default_session_configs:
            return self.default_session_configs[viewType](key, self.provider, identifier)
        raise SessionConfigError('Unknown session type')

    def __setitem__(self, key, item):
        if not isinstance(item, SessionConfig):
            raise TypeError('item must be of type SessionConfig')
        return dict.__setitem__(self, key, item)

class Sprocket:
    """Association between a view and a sessionConfig"""

    def __init__(self, view, session):
        """Construct a Sprocket Object

        view
            a ``view`` object which has been instantiated from a ``ViewConfig``
        session
            a ``sessionConfig`` object which contains the method for obtaining data for the associated view.
        """

        if not isinstance(view, View):
            raise TypeError('view is not of type View')
        if not isinstance(session, SessionConfig):
            raise TypeError('session is not of type SessionConfig')
        self.session = session
        self.view = view

class Sprockets(dict):
    """Set of Associations between widgets and the method to obtain their data"""

    def __init__(self, provider, controller):
        """Construct a Sprockets Object

        provider
            a ``IProvider`` object to instantiate views with.  Usually this is an SAProvider

        controller
            String.  This is a link to the URL in the application where the view is intended to
            be mounted.  I am hoping this is eliminated in the future.  Right now this is needed
            for some widgets to provide links to the interface.
        """

        if not isinstance(provider, IProvider):
            raise TypeError('provider is not of type IProvider')
        if not isinstance(controller, types.StringTypes):
            raise TypeError('controller is not of type String')
        self.views = Views(provider, controller)
        self.sessions = Sessions(provider)
        self.controller = controller

    def __getitem__(self, key):
        if key in self:
            return dict.__getitem__(self, key)
        sprocket = self._get_sprocket(key)
        self[key] = sprocket
        return sprocket

    def _get_sprocket(self, key):
        view = self.views[key]
        session = self.sessions[key]
        return Sprocket(view, session)

    def __setitem__(self, key, item):
        if not isinstance(item, Sprocket):
            raise TypeError('item must be of type Sprocket')
        return dict.__setitem__(self, key, item)
