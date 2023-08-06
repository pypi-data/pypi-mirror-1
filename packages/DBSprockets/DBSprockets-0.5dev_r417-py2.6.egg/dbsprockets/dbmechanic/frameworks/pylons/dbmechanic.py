"""
dbmechanic module for Pylons

Initial version by Isaac Csandl <nerkles _at_ gmail {d0t} com> based on the tg2 version.

"""
import os
import pkg_resources
import sqlalchemy
from tw.api import Widget
import pylons
from pylons.templating import cached_template, pylons_globals
from pylons.controllers import WSGIController
from pylons import c, request
from dbsprockets.sprockets import Sprockets
#from dbsprockets.decorators import crudErrorCatcher, validate
from tw.api import WidgetBunch
from genshi.template import TemplateLoader


def render_genshi(template_name, genshi_loader, cache_key=None, cache_type=None,
                  cache_expire=None, fragment=False, format='xhtml'):
    """
    Copied out of Pylons so that we can specify the path to genshi templates.

    Render a template with Genshi

    Accepts the cache options ``cache_key``, ``cache_type``, and
    ``cache_expire`` in addition to fragment and format which are
    passed to Genshi's render function.

    """
    # Create a render callable for the cache function
    def render_template():
        # First, get the globals
        globs = pylons_globals()

        # Grab a template reference
        template = genshi_loader.load(template_name)

        return template.generate(**globs).render()

    return cached_template(template_name, render_template, cache_key=cache_key,
                           cache_type=cache_type, cache_expire=cache_expire,
                           ns_options=('fragment', 'format'),
                           fragment=fragment, format=format)


class DBMechanic(WSGIController):
    sprockets = None
    def __init__(self, provider, controller, *args, **kwargs):
        self.provider = provider
        self.sprockets = Sprockets(provider, controller)
        self.controller = controller
        #commonly used views
        c.w = WidgetBunch()
        sprocket = self.sprockets['databaseView']
        self.databaseValue = sprocket.session.get_value()
        self.databaseView  = sprocket.view.widget
        print 'controller:', self.controller

        self.databaseDict  = dict(controller=self.controller)
        self.genshi_loader = TemplateLoader([pkg_resources.resource_filename('dbsprockets.dbmechanic.frameworks.pylons', 'templates')])
        WSGIController.__init__(self, *args, **kwargs)

    def index(self):
        c.w.databaseView  = self.databaseView
        c.w.mainView=Widget("widget")
        return render_genshi('index.html', self.genshi_loader)


    def tableDef(self, id): #table_name):
        c.table_name = id
        sprocket  = self.sprockets['table_def__'+c.table_name]
        c.w.mainView  = sprocket.view.widget
        c.w.databaseView  = self.databaseView
        c.mainValue = sprocket.session.get_value()
        for key, value in self.databaseDict.iteritems():
            setattr(c, key, value)
        return render_genshi('index.html', self.genshi_loader)

    def tableView(self, id):
        c.table_name = id
        c.page = request.params.get('page', 1)
        c.recordsPerPage = request.params.get('recordsPerPage', 25)
        #this should probably be a decorator
        c.page = int(c.page)
        c.recordsPerPage = int(c.recordsPerPage)
        sprocket  = self.sprockets['table_view__'+c.table_name]
        c.w.mainView  = sprocket.view.widget
        c.w.databaseView  = self.databaseView
        c.mainValue = sprocket.session.get_value(values=request.params, page=c.page, recordsPerPage=c.recordsPerPage)
        c.main_count = sprocket.session.get_count(values=request.params)
        for key, value in self.databaseDict.iteritems():
            setattr(c, key, value)
        return render_genshi('tableView.html', self.genshi_loader)

    def addRecord(self, id): #table_name, **kw):
        c.table_name = id
        sprocket = self.sprockets['add_record__'+c.table_name]
        c.w.mainView  = sprocket.view.widget
        c.w.databaseView  = self.databaseView
        kw = {}
        for key, value in request.params.iteritems():
            if key and value:
                setattr(kw, key, value)
        c.mainValue = sprocket.session.get_value(values=kw)
        for key, value in self.databaseDict.iteritems():
            setattr(c, key, value)
        return render_genshi('index.html', self.genshi_loader)

    def editRecord(self, id): #table_name, **kw):
        c.table_name = request.params.get('table_name', None)
        sprocket = self.sprockets['edit_record__'+c.table_name]
        c.w.mainView  = sprocket.view.widget
        c.w.databaseView  = self.databaseView
        kw = {}
        kw.update(request.params.__dict__)
        c.mainValue = sprocket.session.get_value(values=kw)
        for key, value in self.databaseDict.iteritems():
            setattr(c, key, value)
        return render_genshi('index.html', self.genshi_loader)

    def _createRelationships(self, table_name, params):
        #this might become a decorator
        #check to see if the table is a many-to-many table first
        if table_name in self.provider.get_many_to_many_tables():
            return
        #right now many-to-many only supports single primary keys
        id = params[self.provider.get_primary_keys(table_name)[0]]
        relationships = {}
        for key, value in params.iteritems():
            if key.startswith('many_many_'):
                relationships.setdefault(key[10:], []).append(value)
        for key, value in relationships.iteritems():
            self.provider.set_many_to_many(table_name, id, key, value)

    # @validate(error_handler=editRecord)
    #@crudErrorCatcher(errorType=sqlalchemy.exceptions.IntegrityError, error_handler='editRecord')
    #@crudErrorCatcher(errorType=sqlalchemy.exceptions.ProgrammingError, error_handler='editRecord')
    def edit(self, id): # table_name, *args, **kw):
        table_name = request.params.get('table_name', None)
        params = pylons.request.params.copy()
        self._createRelationships(table_name, params)
        self.provider.edit(table_name, values=params)
        raise redirect(self.controller+'/tableView/'+table_name)

    # @validate(error_handler=addRecord)
    #@crudErrorCatcher(errorType=sqlalchemy.exceptions.IntegrityError, error_handler='addRecord')
    #@crudErrorCatcher(errorType=sqlalchemy.exceptions.ProgrammingError, error_handler='addRecord')
    def add(self, id): #table_name, **kw):
        table_name = request.params.get('table_name', None)
        params = pylons.request.params.copy()
        self._createRelationships(table_name, params)
        self.provider.add(table_name, values=params)
        raise redirect(self.controller+'/tableView/'+table_name)

    def delete(self, id): # table_name, **kw):
        table_name = request.params.get('table_name', None)
        self.provider.delete(table_name, values=kw)
        raise redirect(self.controller+'/tableView/'+table_name)
