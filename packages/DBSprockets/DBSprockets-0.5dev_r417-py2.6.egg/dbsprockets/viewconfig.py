"""
ViewConfig Module

The ViewConfig defines all of the View related issues for dbsprockets

Classes:
Name                               Description
ViewConfig                         Parent Class
DatabaseViewConfig
EditRecordConfig
TableDefViewConfig
TableViewConfig
AddRecordViewConfig

Exceptions:
None

Functions:
None

Copywrite (c) 2007 Christopher Perkins
Original Version by Christopher Perkins 2007
Released under MIT license.
"""
import types
from cStringIO import StringIO
from tw.forms.fields import HiddenField
from tw.api import Widget
from tw.forms import DataGrid, TableForm, SingleSelectField, TextField, FieldSet
from copy import copy
from urllib import quote
from genshi.input import HTML, XML

from dbsprockets.validatorselector import ValidatorSelector, SAValidatorSelector
from dbsprockets.widgetselector import *
from dbsprockets.widgets.widgets import *
from dbsprockets.metadata import *
from dbsprockets.iprovider import IProvider
from tw.forms.validators import String,Int
from formencode.compound import All
from formencode import Schema

class FilteringSchema(Schema):
    filter_extra_fields = True
    allow_extra_fields = True

from tw.forms.fields import SingleSelectField

class ViewConfigMeta(object):
    _hidden_fields     = []
    _disabled_fields   = []
    _required_fields   = []
    _omitted_fields    = []
    _field_order       = None

    limit_fields = None

    validator_selector_type = ValidatorSelector
    widget_validator  = None
    check_if_unique  = False

    _field_widgets     = {}
    _field_attrs       = {}
    _field_validators  = {}
    _additional_fields = {}
    _field_widget_types = {}

    widget_type = Widget
    widget_selector_type = WidgetSelector

    metadata_type = Metadata

    def __new__(cls, *args, **kw):
        bases = cls.mro()
        chained_attrs = ['_hidden_fields', '_required_fields', '_disabled_fields', '_omitted_fields']
        for base in bases:
            for attr in chained_attrs:
                if hasattr(base, attr):
                    current =  getattr(cls, attr)
                    setattr(cls, attr, current + [item for item in getattr(base, attr) if item not in current])
        return object.__new__(cls, *args, **kw)

    def __init__(self, provider, identifier=None, controller='/'):
        """(metadata, controller)"""
        if not isinstance(provider, IProvider):
            raise TypeError('arg1 should be an IProvider, not a : %s', type(provider))
        if not isinstance(identifier, types.StringTypes):
            raise TypeError('arg2 should be a String, not a: %s', type(identifier))
        if not isinstance(controller, types.StringTypes):
            raise TypeError('arg3 should be a String,  not a: %s', type(controller))

        self.provider = provider
        self.identifier = identifier
        self.controller = controller
        self.metadata = self.metadata_type(provider, identifier)
        self.widget_selector = self._do_get_widget_selector()
        self.validator_selector = self.validator_selector_type(provider)

        self.__hidden_fields     = copy(self._hidden_fields)
        self.__disabled_fields   = copy(self._disabled_fields)
        self.__required_fields   = copy(self._required_fields)
        self.__omitted_fields    = copy(self._omitted_fields)
        self.additional_fields = copy(self._additional_fields)


        self.field_order         = copy(self._field_order)
        self.field_widgets       = copy(self._field_widgets)
        self.field_widget_types  = copy(self._field_widget_types)
        self.field_attrs         = copy(self._field_attrs)
        self.field_validators    = copy(self._field_validators)

    def _get_omitted_fields(self):
        return self.__omitted_fields
    def _set_omitted_fields(self, item):
        self.__omitted_fields = item
    omitted_fields = property(_get_omitted_fields, _set_omitted_fields)

#    def _get_additional_fields(self):
#        return self.__additional_fields
#    def _set_additional_fields(self, item):
#        self.__additional_fields = item
#    additional_fields = property(_get_additional_fields, _set_additional_fields)

    def _get_disabled_fields(self):
        fields =  self.__disabled_fields
        fields.extend([field for field in self._do_get_disabled_fields() if field not in fields])
        return fields
    def _set_disabled_fields(self, item):
        self.__disabled_fields = item
    disabled_fields = property(_get_disabled_fields, _set_disabled_fields)

    def _get_required_fields(self):
        return self.__required_fields
    def _set_required_fields(self, item):
        self.__required_fields = item
    required_fields = property(_get_required_fields, _set_required_fields)

    def _get_hidden_fields(self):
        return self.__hidden_fields
    def _set_hidden_fields(self, item):
        self.__hidden_fields = item
    hidden_fields = property(_get_hidden_fields, _set_hidden_fields)

    @property
    def many_to_many_fields(self):
        return self._do_get_many_to_many_fields()

    @property
    def fields(self):
        return self._do_get_fields()

    def _remove_duplicates(self, l):
        l2 = []
        for i in l:
            if i not in l2:
                l2.append(i)
        return l2

    def _do_get_fields(self):
        fields = []
        if self.field_order is not None:
            #this makes sure all the ordered fields bubble to the start of the list
            fields.extend(self.field_order)
        if self.limit_fields is not None:
            fields.extend(self.limit_fields)
            fields.extend(self.hidden_fields)
            fields = self._remove_duplicates(fields)
            return fields
        else:
            fields = self.metadata.keys()

        fields.extend(self.additional_fields.keys())
        fields.extend(self.hidden_fields)

        if self.field_order is not None:
            fields = set(fields)
            field_order = set(self.field_order)
            extra_fields = fields.difference(field_order)
            fields = self.field_order+list(extra_fields)

        fields.extend(self.many_to_many_fields)

        for field in self.omitted_fields:
            if field in fields:
                fields.remove(field)

        #remove all duplicate fields
        r = []
        for field in fields:
            if field not in r:
                r.append(field)
        return r

    def _get_field_widgets(self, fields, validators):
        field_attrs = self.field_attrs
        hidden_fields = self.hidden_fields
        disabled_fields = self.disabled_fields
        required_fields = self.required_fields
        omitted_fields = self.omitted_fields
        field_widgets = self.field_widgets
        many_to_many_fields = self.many_to_many_fields
        additional_fields = self.additional_fields

        widgets = {}
        for field_name in fields:
            if field_name in field_widgets:
                widgets[field_name] = field_widgets[field_name]
                #we need to re-instantiate the widget if it does not have a validator so that
                #we can add our own validator in here.
                continue
            if field_name in additional_fields:
                widgets[field_name] = additional_fields[field_name]
                #we need to re-instantiate the widget if it does not have a validator so that
                #we can add our own validator in here.
                continue
            if field_name in omitted_fields:
                continue
            if field_name in many_to_many_fields:
                continue
            if field_name == 'dbsprockets_id':
                continue
            if field_name in hidden_fields:
                continue

            field = self.metadata[field_name]
            widget_type = self.field_widget_types.get(field_name, self.widget_selector.select(field))
            child_widget_args = self._do_get_child_widget_args_for_widget_type(field, widget_type)
            child_widget_args.update({'id':field_name.replace('.','_'), 'identifier':field})

            if field_name in required_fields:
                child_widget_args['required'] = True
            if field in field_attrs:
                child_widget_args['attrs'] = field_attrs.get[field_name]
            child_val=validators.get(field_name, None)
            if child_val:
                child_widget_args['validator'] = child_val
            if field_name in disabled_fields:
                child_widget_args['disabled'] = True
                widgets[field_name] = (HiddenField(id=field_name.replace('.','_'), identifier=field_name), widget_type(**child_widget_args))
                continue
            widgets[field_name] = widget_type(**child_widget_args)

        widgets.update(self._create_hidden_fields())
        widgets.update(self._do_get_many_to_many_widgets(many_to_many_fields))
        return widgets

    def _get_field_validators(self):
        validators = {}
        return validators

    #def _create_disabled_fields(self):
    #    fields = {}
    #    for field in self.disabled_fields:
    #        if field not in self.omitted_fields and field not in self.hidden_fields:
    #            fields[field] = HiddenField(id=field, identifier=field)
    #    return fields

    def _create_hidden_fields(self):
        fields = {}
        fields['dbsprockets_id'] = HiddenField(id='dbsprockets_id')

        for field in self.hidden_fields:
            if field not in self.omitted_fields:
                fields[field] = HiddenField(id=field, identifier=field)

        return fields

    def _get_field_validators(self, fields):
        disabled_fields = self.disabled_fields
        required_fields = self.required_fields
        omitted_fields = self.omitted_fields
        hidden_fields = self.hidden_fields
        validator_overrides = self.field_validators
        many_to_many_fields = self.many_to_many_fields
        check_if_unique = self.check_if_unique
        additional_fields = self.additional_fields

        validators={}
        for field_name in fields:
            if field_name in omitted_fields:
                continue
            if field_name in many_to_many_fields:
                continue
            if field_name == 'dbsprockets_id':
                continue
            if field_name in hidden_fields:
                continue
            if field_name in additional_fields:
                continue

            field = self.metadata[field_name]
            validator = None
            if field_name not in disabled_fields:
                if field_name in validator_overrides:
                    validator = validator_overrides[field_name]
                else:
                    validator = self.validator_selector.select(field, (field_name in required_fields), check_if_unique)

            validators[field_name] = validator

            if field_name in disabled_fields:
                validators[field_name] = String(if_missing=None)

        return validators

    def get_widget_args(self, id=None):
        field_validators = self._get_field_validators(self.fields)
        widget_dict = self._get_field_widgets(self.fields, field_validators)

        field_widgets = []
        for key in self.fields:
            value = widget_dict[key]
            #sometimes a field will have two widgets associated with it (disabled fields)
            if hasattr(value,'__iter__'):
                field_widgets.extend(value)
                continue
            field_widgets.append(value)

        d = dict(children=field_widgets)
        d['controller'] = self.controller
        if self.widget_validator:
            d['validator'] = self.widget_validator
        else:
            d['validator'] = FilteringSchema
        d.update(self._do_add_extra_widget_args())
        return d

    @property
    def action(self):
        return self._do_get_action()

    def _do_get_many_to_many_fields(self):
        return []
    def _do_get_action(self):
        raise NotImplementedError
    def _do_add_extra_widget_args(self):
        return {}
    def _do_get_widget_selector(self):
        return self.widget_selector_type()
    def _do_get_child_widget_args_for_widget_type(self, field, widget_type):
        return {}
    def _do_get_many_to_many_widgets(self, fields):
        return {}
    def _do_get_disabled_fields(self):
        return []

class ViewConfig(ViewConfigMeta):pass

class DatabaseViewConfig(ViewConfig):
    widget_type = ContainerWidget
    metadata_type = DatabaseMetadata
    widget_selector_type = DatabaseViewWidgetSelector

class TableDefViewConfig(ViewConfig):
    widget_type = TableWidget
    metadata_type = FieldsMetadata
    widget_selector_type = TableDefWidgetSelector

class RecordViewConfig(ViewConfig):
    widget_type = RecordViewWidget
    metadata_type = FieldsMetadata
    widget_selector_type = RecordViewWidgetSelector

class TableViewConfig(ViewConfig):
    widget_type = DataGrid
    metadata_type = FieldsMetadata
    foreign_key_field_labels = ['name', '_name', 'description', '_description', 'title']

    def _writePKsToURL(self, pks, row):
        stream = StringIO()
        l = len(pks) - 1
        for i, pk in enumerate(pks):
            if i == 0:
                stream.write('?')
            else:
                stream.write('&')
            stream.write(str(pk))
            stream.write('=')
            value=row[pk]
            if hasattr(value,"original"):
                value=value.original
            if isinstance(value, unicode):
                value=value.encode('utf8')
            value=quote(str(value))
            stream.write(value)

        return stream.getvalue()

    def _make_links(self, row):
        pks = self.metadata.primary_keys()
        editLink = StringIO()
        editLink.write('<a href="')
        editLink.write(self.controller+'/editRecord/')
        editLink.write(self.metadata.identifier)
        editLink.write(self._writePKsToURL(pks, row))
        editLink.write('">edit</a>')

        delete_link = StringIO()
        delete_link.write('<a href="')
        delete_link.write(self.controller+'/delete/')
        delete_link.write(self.metadata.identifier)
        delete_link.write(self._writePKsToURL(pks, row))
        delete_link.write('">delete</a>')
        editLink.write('|')
        editLink.write(delete_link.getvalue())
        return HTML(editLink.getvalue())

    def get_widget_args(self):
        fields = self.fields
        pks  = self.metadata.primary_keys()
        omitted_fields = self.omitted_fields
        fields = [(field, eval('lambda d: d["'+field+'"]')) for field in fields if field not in omitted_fields]
        if '_actions' not in omitted_fields:
            fields.insert(0, (' ', self._make_links))
        many_to_many_tables = self.provider.get_many_to_many_tables()
        if self.identifier not in many_to_many_tables:
            many_to_many_columns = self.provider.get_many_to_many_columns(self.identifier)
            fields.extend([('%s'%table, eval('lambda d: d["'+table+'"]')) for table in many_to_many_columns])
        return dict(id=self.__class__.__name__, fields=fields)

class EditableRecordViewConfig(ViewConfig):
    widget_type = DBSprocketsTableForm
    metadata_type = FieldsMetadata
    widget_selector_type = SAWidgetSelector
    validator_selector_type = SAValidatorSelector
    _hidden_fields     = ['table_name']
    _action = ''

    def _do_get_fields(self):
        fields = super(EditableRecordViewConfig, self)._do_get_fields()
        if 'dbsprockets_id' not in fields:
            fields.append('dbsprockets_id')
        return fields

    def _do_get_action(self):
        return self._action

    def _do_add_extra_widget_args(self):
        return dict(action=self.action)

    def _do_get_disabled_fields(self):
        return self.metadata.primary_keys()

    def _do_get_many_to_many_fields(self):
        associatedTables = self.provider.get_associated_many_to_many_tables(self.identifier)
        return [table+'s' for table in associatedTables]

    def _do_get_many_to_many_widgets(self, fields):
        table_name = self.identifier
        widgets = {}
        omitted_fields = self.omitted_fields
        hidden_fields  = self.hidden_fields
        limit_fields   = self.limit_fields
        for field_name in fields:
            table = field_name[:-1]
            if not (field_name in hidden_fields ) and \
               not (field_name in omitted_fields) and \
                   ((limit_fields is None) or (field_name in limit_fields)):
                        widgets[field_name] = ForeignKeyMultipleSelectField(id="many_many_"+table, label_text=field_name, table_name=table, provider=self.provider)
        return widgets

    def _do_get_child_widget_args_for_widget_type(self, field, widget_type):
        if widget_type == ForeignKeySingleSelectField:
            nullable=self.provider.is_nullable_field(field)
            return dict(nullable=nullable, validator=String(if_missing=None), provider=self.provider, table_name=field.foreign_keys[0].column.table.name)
        if widget_type==TextField and hasattr(field.type, 'length') and (not field.type.length is None):
            max_length=field.type.length
            if field.type.length>80:
                size=80
            else:
                size=field.type.length
            return dict(size=size, maxlength=max_length)
        return {}

class EditRecordViewConfig(EditableRecordViewConfig):
    widget_type = DBSprocketsTableForm
    metadata_type = FieldsMetadata
    widget_selector_type = SAWidgetSelector
    validator_selector_type = SAValidatorSelector
    _hidden_fields     = ['table_name']

    def _do_get_action(self):
        return self.controller+'/edit'


class AddRecordViewConfig(EditRecordViewConfig):
    check_if_unique = True
    def _do_get_action(self):
        return self.controller+'/add'

    def _do_get_disabled_fields(self):
        foreign_keys=self.metadata.foreign_keys

        return [k for k in self.metadata.primary_keys() if ((k in self.metadata.auto_increment_fields) or self.metadata.get_server_default(k)) and not k in foreign_keys]
