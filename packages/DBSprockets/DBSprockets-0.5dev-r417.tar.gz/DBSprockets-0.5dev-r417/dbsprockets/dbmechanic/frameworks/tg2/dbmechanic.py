"""
dbmechanic Module

this contains a turbogears controller which allows the user to have a
phpMyAdmin *cringe*-like interface.  It is intended to be a replacement
for Catwalk

Classes:
Name                               Description
DBMechanic

Exceptions:
None

Functions:
None

Copywrite (c) 2007 Christopher Perkins
Original Version by Christopher Perkins 2007
Released under MIT license.
"""
import sqlalchemy
from tg.decorators import expose
from tg.controllers import redirect, DecoratedController
from tw.api import Widget, CSSLink, Link
import pylons

from dbsprockets.sprockets import Sprockets
from tg import TGController
from dbsprockets.decorators import crudErrorCatcher, validate

dbsprocketsCss = CSSLink(modname='dbsprockets', filename='dbmechanic/static/css/dbmechanic.css')
dbMechanicFooterImg = Link(modname='dbsprockets', filename='dbmechanic/static/images/grad_blue.png')

class BaseController(TGController):
    """Basis TurboGears controller class which is derived from
    TGController
    """

    def __call__(self, environ, start_response):
        """Invoke the Controller"""
        # TGController.__call__ dispatches to the Controller method
        # the request is routed to. This routing information is
        # available in environ['pylons.routes_dict']

        # Create a container to send widgets to the template. Only those sent
        # in here will have their resources automatically included in the
        # template
        try:
            dbMechanicFooterImg.inject()
            return TGController.__call__(self, environ, start_response)
        finally:
            pass
            #after everything is done clear out the Database Session
            #so to eliminate possible cross request DBSession polution.
            #model.DBSession.remove()

class DBMechanic(BaseController):
    sprockets = None
    def __init__(self, provider, controller, *args, **kwargs):
        self.provider = provider
        self.sprockets = Sprockets(provider, controller)
        self.controller = controller

        #commonly used views
        sprocket = self.sprockets['database_view']
        self.databaseValue = sprocket.session.get_value()
        self.databaseView  = sprocket.view.widget
        self.databaseDict  = dict(databaseValue=self.databaseValue, controller=self.controller)
        BaseController.__init__(self, *args, **kwargs)

    @expose('genshi:dbsprockets.dbmechanic.frameworks.tg2.templates.index')
    def index(self):
        dbsprocketsCss.inject()
        pylons.c.databaseView  = self.databaseView
        pylons.c.mainView=Widget("widget")
        return self.databaseDict

    @expose('genshi:dbsprockets.dbmechanic.frameworks.tg2.templates.edit')
    def tableDef(self, table_name):
        dbsprocketsCss.inject()
        sprocket  = self.sprockets['table_def__'+table_name]
        pylons.c.mainView  = sprocket.view.widget
        pylons.c.databaseView  = self.databaseView
        mainValue = sprocket.session.get_value()
        d = dict(table_name=table_name, mainValue=mainValue)
        d.update(self.databaseDict)
        return d

    @expose('genshi:dbsprockets.dbmechanic.frameworks.tg2.templates.tableView')
    def tableView(self, table_name, page=1, recordsPerPage=25, **kw):
        dbsprocketsCss.inject()
        #this should probably be a decorator
        page = int(page)
        recordsPerPage = int(recordsPerPage)

        sprocket  = self.sprockets['table_view__'+table_name]
        pylons.c.mainView  = sprocket.view.widget
        pylons.c.databaseView  = self.databaseView
        mainValue = sprocket.session.get_value(values=kw, page=page, recordsPerPage=recordsPerPage)
        main_count = sprocket.session.get_count(values=kw,)
        d = dict(table_name=table_name, mainValue=mainValue, main_count=main_count)
        d.update(self.databaseDict)
        d['page'] = page
        d['recordsPerPage'] = recordsPerPage
        return d

    @expose('genshi:dbsprockets.dbmechanic.frameworks.tg2.templates.edit')
    def addRecord(self, table_name, **kw):
        dbsprocketsCss.inject()
        sprocket = self.sprockets['add_record__'+table_name]
        pylons.c.mainView  = sprocket.view.widget
        pylons.c.databaseView  = self.databaseView
        mainValue = sprocket.session.get_value(values=kw)
        d = dict(table_name=table_name, mainValue=mainValue)
        d.update(self.databaseDict)
        return d

    @expose('genshi:dbsprockets.dbmechanic.frameworks.tg2.templates.edit')
    def editRecord(self, table_name, **kw):
        dbsprocketsCss.inject()
        sprocket = self.sprockets['edit_record__'+table_name]
        pylons.c.mainView  = sprocket.view.widget
        pylons.c.databaseView  = self.databaseView
        mainValue = sprocket.session.get_value(values=kw)
        d = dict(table_name=table_name, mainValue=mainValue)
        d.update(self.databaseDict)
        return d

    @expose()
    @validate(error_handler=editRecord)
    @crudErrorCatcher(errorType=sqlalchemy.exceptions.IntegrityError, error_handler='editRecord')
    @crudErrorCatcher(errorType=sqlalchemy.exceptions.ProgrammingError, error_handler='editRecord')
    @crudErrorCatcher(errorType=sqlalchemy.exceptions.DataError, error_handler='editRecord')
    def edit(self, table_name, *args, **kw):
        params = pylons.request.params.copy()
        self.provider.create_relationships(table_name, params)

        self.provider.edit(table_name, values=kw)
        redirect(self.controller+'/tableView/'+table_name)

    @expose()
    @validate(error_handler=addRecord)
    @crudErrorCatcher(errorType=sqlalchemy.exceptions.IntegrityError, error_handler='addRecord')
    @crudErrorCatcher(errorType=sqlalchemy.exceptions.ProgrammingError, error_handler='addRecord')
    def add(self, table_name, **kw):
        params = pylons.request.params.copy()
        self.provider.create_relationships(table_name, params)

        self.provider.add(table_name, values=kw)
        redirect(self.controller+'/tableView/'+table_name)

    @expose()
    def delete(self, table_name, **kw):
        self.provider.delete(table_name, values=kw)
        redirect(self.controller+'/tableView/'+table_name)
