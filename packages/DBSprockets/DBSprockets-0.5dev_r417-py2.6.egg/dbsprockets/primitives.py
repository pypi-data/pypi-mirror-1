"""
primitives Module

short cut functions for dbsprocket form creation

Classes:
Name                               Description
None

Exceptions:
None

Functions:
make_form        make a form for user entry
make_table       make a table for user values
make_view        view helper function
get_table_values  helper to get table values


Copywrite (c) 2007 Christopher Perkins
Original Version by Christopher Perkins 2007
Released under MIT license.
"""
import new

from dbsprockets.saprovider import SAProvider
from dbsprockets.viewconfig import RecordViewConfig, TableViewConfig, EditableRecordViewConfig
from dbsprockets.viewfactory import ViewFactory
from dbsprockets.sessionconfig import TableViewSessionConfig
import types
from formencode.schema import Schema
from tw.forms import TableForm
import sqlalchemy
from sqlalchemy.orm import class_mapper
from dbsprockets.util import freshdefaults

try:
    from sqlalchemy.orm.attributes import ClassManager
except:
    from warnings import warn
    warn('Versions of dbsprockets>=0.5 will require sqlalchemy>=0.5')

class DBHelper:
    def __init__(self):
        self._identifiers = {}
        self._metadata = None
        self._provider = None

    def get_metadata(self, model):
        raise NotImplementedError

    def get_identifier(self, model):
        raise NotImplementedError

    def validate_model(self, model):
        raise NotImplementedError

class _SAORMDBHelper(DBHelper):

    def _mapper(self,model):
        return class_mapper(model)

    def _first_column(self, model):
        mapper = self._mapper(model)
        return mapper.c[mapper.c.keys()[0]]

    def get_metadata(self, model):
        firstColumn = self._first_column(model)
        if self._metadata is None:
            self._metadata = firstColumn.metadata
            self._identifiers[model] = firstColumn.table.name
        return self._metadata

    def get_identifier(self, model):
        if model not in self._identifiers:
            self._identifiers[model] = self._first_column(model).table.name
        return self._identifiers[model]

    def get_provider(self, model):
        if self._provider is None:
            self._provider = SAProvider(self.get_metadata(model))
        return self._provider

    def validate_model(self, model):
        if not hasattr(model, '_sa_class_manager') or not isinstance(model._sa_class_manager, ClassManager):
            raise TypeError('arg1(%s) has not been mapped to an sql table appropriately'%model)

        #failsafe, return a form with nothing in it
        if self._mapper(model).c.keys() == 0:
            raise Exception('Form has no fields')

SAORMDBHelper = _SAORMDBHelper()

#XXX:
#StormHelper = _StormHelper()
#SOHelper    = _SOHelper()

class DatabaseMixin(object):
    def __init__(self, db_helper=None):
        self._db_helper = db_helper

    def _get_helper(self, model):
        if self._db_helper is None:

            #use a SA Helper
            if hasattr(model, '_sa_class_manager') and isinstance(model._sa_class_manager, ClassManager):
                self._db_helper = SAORMDBHelper
            #other helper definitions are going in here
            else:
                raise Exception('arg1(model) has not been mapped to an sql table appropriately')
        return self._db_helper

    def _validate_model(self, model):
        helper = self._get_helper(model)
        helper.validate_model(model)

class SprocketGenerator(DatabaseMixin):

    def make_form(self,
                 model,
                 action,
                 identifier='',
                 controller='/',
                 field_order=None,
                 hidden_fields=None,
                 disabled_fields=None,
                 required_fields=None,
                 omitted_fields=None,
                 additional_fields=None,
                 limit_fields=None,
                 field_attrs=None,
                 widgets=None,
                 validators=None,
                 form_widget_type=None,
                 form_validator=None,
                 check_if_unique=False,
                 ):
        """
        make_form(model,
                 action,
                 identifier='',
                 identifier='',
                 controller='/',
                 hidden_fields=[],
                 disabled_fields=[],
                 required_fields=[],
                 omitted_fields=[],
                 additional_fields={},
                 limit_fields=None,
                 field_attrs={},
                 widgets={},
                 validators={},
                 form_widget_type=None,
                 form_validator=None
                 check_if_unique=False)-->tw.forms.TableForm

        Generates an entry form for use in web applications.

        Arguments:
        name              type                           default    Description
        model             class                                     sqlalchemy mapped class definition
        action            String                                    string passed to the forms 'action'
        identifier        String or None                 None       optional identifier for the form
        field_order       list of names                  None       order of the fields to be rendered (hidden fields will always render first)
        hidden_fields      list if names                  []         fields that are hidden but not altogether
                                                                    removed from the table, useful for passing
                                                                    data through a form manually.
        disabled_fields    list of names                  []         fields that are shown but not editable
        required_fields    list of names                  []         fields that cannot be left empty by the user (validation type stuff)
        omitted_fields     list of names                  []         fields that are not present, whatsoever
        additional_fields  dict of Toscawidgets.fields  {}    fields that you would like to add to the form that are not in the model the key is the field name
        limit_fields       list of names                  None       limit the fields to the one in the list.  A side effect is that the
                                                                    order of the fields is set by this argument.
                                                                    (a good way to order your fields if you include all of them)
        field_attrs        dict of field Attrs            {}         a set of extra parameters which can be passed into the widgets
                                                                    that are created in a form.
        widgets           dict of Toscawidgets           {}         a set of widgets linked to your fields by fieldname, you must do your own validation.
        validators        dict of formencode.validators  {}         validators linked to fields in your form indexed by fieldname
        form_widget_type    ToscaWidget                    None       field for the actual widget to be used
        form_validator     Schema or validator            None       validator for the overall form
        check_if_unique     Boolean                        False      adds default validator to "unique" fields to check if the value
                                                                    the user has entered is unique or not.
        """
        if hidden_fields is None:
            hidden_fields = []
        if disabled_fields is None:
            disabled_fields=[]
        if required_fields is None:
            required_fields=[]
        if omitted_fields is None:
            omitted_fields=[]
        if additional_fields is None:
            additional_fields={}
        if field_attrs is None:
            field_attrs={}
        if widgets is None:
            widgets={}
        if validators is None:
            validators={}


        if not isinstance(action, types.StringTypes):
            raise TypeError('arg2(action) must be of type String, not %s'%type(action))
        if not isinstance(controller, types.StringTypes):
            raise TypeError('arg3(controller) must be of type String, not %s'%type(action))
        if not isinstance(identifier, types.StringTypes):
            raise TypeError('arg4(action) must be of type String, not %s'%type(action))
        if not isinstance(hidden_fields, types.ListType):
            raise TypeError('arg6(hidden_fields) must be of type List, not %s'%type(hidden_fields))
        if not isinstance(disabled_fields, types.ListType):
            raise TypeError('arg7(disabled_fields) must be of type List, not %s'%type(disabled_fields))
        if not isinstance(omitted_fields, types.ListType):
            raise TypeError('arg8(omitted_fields) must be of type List, not %s'%type(omitted_fields))
        if not isinstance(additional_fields, types.DictType):
            raise TypeError('arg9(additional_fields) must be of type Dict, not %s'%type(additional_fields))
        if limit_fields is not None and not isinstance(limit_fields, types.ListType):
            raise TypeError('arg10(limit_fields) must be of type List, not %s'%type(limit_fields))
        if not isinstance(field_attrs, types.DictType):
            raise TypeError('arg11(field_attrs) must be of type Dict, not %s'%type(limit_fields))
        if not isinstance(validators, types.DictType):
            raise TypeError('arg12(validators) must be of type Dict, not %s'%type(validators))
        if form_validator is not None and not isinstance(form_validator, Schema):
            raise TypeError('arg13(form_validator) must be of type Dict, not %s'%type(form_validator))
        if not isinstance(check_if_unique, bool):
            raise TypeError('arg14(check_if_unique) must be of type bool, not %s'%type(check_if_unique))

        self._validate_model(model)

        view = self.make_view(EditableRecordViewConfig,
                        model,
                        action,
                        identifier,
                        '',
                        field_order,
                        hidden_fields,
                        disabled_fields,
                        required_fields,
                        omitted_fields,
                        additional_fields,
                        limit_fields,
                        field_attrs,
                        widgets,
                        validators,
                        form_widget_type,
                        form_validator,
                        check_if_unique)
        return view.widget

    def make_record_view(self,
                 model,
                 controller='',
                 field_order=None,
                 omitted_fields=None,
                 additional_fields=None,
                 limit_fields=None,
                 field_attrs=None,
                 widgets=None,
                 validators=None,
                 form_widget_type=None,
                 ):
        """
        make_record_view(model,
                 controller='',
                 field_order=None,
                 omitted_fields=[],
                 additional_fields=[],
                 limit_fields=[],
                 field_attrs={},
                 widgets={},
                 validators={},
                 form_widget_type=None,
                )-->Toscawidgets.TableForm

        Generates an entry form for use in web applications.

        Arguments:
        name              type                           default    Description
        model             class                                     sqlalchemy mapped class definition
        identifier        String or None                 None       optional identifier for the form
        controller        String or None                 None       helps with doing links, possibly
        field_order       list of names                  None       order of the fields to be displayed
        omitted_fields     list of names                  []         fields that are not present, whatsoever
        additional_fields  list of Toscawidgets.fields    []         fields that you would like to add to the form that are not in the model
        limit_fields       list of names                  None       limit the fields to the one in the list.  A side effect is that the
                                                                    order of the fields is set by this argument.
                                                                    (a good way to order your fields if you include all of them)
        field_attrs        dict of field Attrs            {}         a set of extra parameters which can be passed into the widgets
                                                                    that are created in a form.
        form_widget_type    ToscaWidget                    None       field for the actual widget to be used
        """
        if omitted_fields is None:
            omitted_fields=[]
        if additional_fields is None:
            additional_fields={}
        if field_attrs is None:
            field_attrs={}
        if widgets is None:
            widgets={}
        if validators is None:
            validators={}

        if not isinstance(omitted_fields, types.ListType):
            raise TypeError('arg7(omitted_fields) must be of type List, not %s'%type(omitted_fields))
        if not isinstance(additional_fields, types.DictType):
            raise TypeError('arg8(additional_fields) must be of type Dict, not %s'%type(additional_fields))
        if limit_fields is not None and not isinstance(limit_fields, types.ListType):
            raise TypeError('arg9(limit_fields) must be of type List, not %s'%type(limit_fields))
        if not isinstance(field_attrs, types.DictType):
            raise TypeError('arg10(field_attrs) must be of type Dict, not %s'%type(limit_fields))

        self._validate_model(model)

        view = self.make_view(RecordViewConfig,
                        model,
                        '',
                        '',
                        controller,
                        field_order=field_order,
                        omitted_fields=omitted_fields,
                        additional_fields=additional_fields,
                        limit_fields=limit_fields,
                        field_attrs=field_attrs,
                        widgets=widgets,
                        widget_type=form_widget_type,
                         )
        return view.widget

    def make_view(self, view_config_type,
                 model,
                 action='',
                 identifier=None,
                 controller='/',
                 field_order=None,
                 hidden_fields=None,
                 disabled_fields=None,
                 required_fields=None,
                 omitted_fields=None,
                 additional_fields=None,
                 limit_fields=None,
                 field_attrs=None,
                 widgets=None,
                 validators=None,
                 widget_type=None,
                 form_validator=None,
                 check_if_unique=False,
                 make_links=None
                 ):
        """this function was added so that you could cache the views more easily if you wanted to use the dbsprockets caching system"""

        if hidden_fields is None:
            hidden_fields = []
        if disabled_fields is None:
            disabled_fields=[]
        if required_fields is None:
            required_fields=[]
        if omitted_fields is None:
            omitted_fields=[]
        if additional_fields is None:
            additional_fields={}
        if field_attrs is None:
            field_attrs={}
        if limit_fields is None:
            limit_fields = []
        if widgets is None:
            widgets={}
        if validators is None:
            validators={}

        helper = self._get_helper(model)
        metadata   = helper.get_metadata(model)
        identifier = helper.get_identifier(model)
        provider   = helper.get_provider(model)

        view_config = view_config_type(provider, identifier)
        view_config._action = action
        attrs = ['required_fields', 'disabled_fields', 'hidden_fields', 'omitted_fields']
        for attr in attrs:
            type_ = locals()[attr]
            fields = getattr(view_config, attr)
            for field in type_:
                if field not in fields:
                    fields.append(field)
        if form_validator:
            view_config.widget_validator = form_validator
        if limit_fields:
            view_config.limit_fields = limit_fields
        if widget_type:
            view_config.widget_type = widget_type
        if field_order:
            view_config.field_order = field_order
        view_config.check_if_unique = check_if_unique
        view_config.field_validators.update(validators)
        view_config.field_widgets.update(widgets)
        view_config.field_attrs.update(field_attrs)
        view_config.additional_fields.update(additional_fields)

        if make_links is not None:
            type_ = type(view_config)
            method = new.instancemethod(make_links, view_config, type_)
            view_config._make_links = method

        view = ViewFactory().create(view_config)
        return view

    def make_table(self, model,
                  controller=None,
                  identifier='',
                  field_order=None,
                  omitted_fields=None,
                  additional_fields=None,
                  limit_fields=None,
                  widget_type=None,
                  make_links=None,
                  ):
        """
        make_table(model,
                 controller=None,
                 identifier='',
                 field_order=None,
                 omitted_fields=[],
                 additional_fields={},
                 limit_fields=None,
                 widetType=None,
                 make_links=None,
                 )-->Toscawidgets.DataGrid

        Generates a datagrid widget for population of database data

        Arguments:
        name              type                           default    Description
        model             class                                     sqlalchemy mapped class definition
        controller        String                                    what controller to send the edit and delete links to.
        identifier        String or None                 None       optional identifier for the form
        field_order       list of names                  None       order of the fields to be rendered
        omitted_fields     list of names                  []         fields that are not present, whatsoever.
                                                                    if '_action' is in the list, then the edit/delete links will be removed.
        additional_fields  dictionary of Toscawidgets.fields  {}    fields that you would like to add to the form that are not in the model the key is the field name
        limit_fields       list of names                  None       limit the fields to the one in the list.  A side effect is that the
                                                                    order of the fields is set by this argument.
                                                                    (a good way to order your fields if you include all of them)
        widget_type        ToscaWidget                    None       field for the parent widget to be used
        make_links         function                       None       Add a custom method for creating action links in your table.
        """
        if omitted_fields is None:
            omitted_fields=[]
        if additional_fields is None:
            additional_fields={}

        self._validate_model(model)
        if controller is None:
            controller = ''
            omitted_fields.append('_actions')

        view = self.make_view(TableViewConfig,
                        model,
                        controller=controller,
                        field_order=field_order,
                        omitted_fields=omitted_fields,
                        additional_fields=additional_fields,
                        widget_type=widget_type,
                        make_links=make_links,
                        limit_fields=limit_fields,
                        )
        return view.widget

class DataFetcher(DatabaseMixin):

    def get_table_value(self, model, offset=None, limit=None, foreign_key_field_labels={}):
        """
        get_table_value(model) --> SQLAlchemy result rows
        gets a set of results for a given model

        xxx: limit and offset are currently not employed

        Arguments:
        name              type                           Description
        model             class                          sqlalchemy mapped class definition
        """

        helper = self._get_helper(model)
        metadata = helper.get_metadata(model)
        identifier = helper.get_identifier(model)
        provider = helper.get_provider(model)
        config = TableViewSessionConfig(identifier+'_session', provider, identifier=identifier)
        return config.get_value()

    def get_form_defaults(self, model):
        """
        get_table_value(model) --> SQLAlchemy result rows
        gets a set of results for a given model

        Arguments:
        name              type                           Description
        model             class                          sqlalchemy mapped class definition
        """

        helper = self._get_helper(model)
        identifier = helper.get_identifier(model)
        provider = helper.get_provider(model)
        return provider.getDefaultValues(identifier)

generator = SprocketGenerator()
fetcher = DataFetcher()

make_form = generator.make_form
make_table = generator.make_table
make_record_view = generator.make_record_view
get_table_value = fetcher.get_table_value
get_form_defaults = fetcher.get_form_defaults

