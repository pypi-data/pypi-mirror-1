from primitives import DatabaseMixin
from formencode.validators import Validator
from tw.api import Widget
import new
from viewfactory import ViewFactory
from viewconfig import ViewConfig, EditableRecordViewConfig, TableDefViewConfig, TableViewConfig, RecordViewConfig, DatabaseViewConfig

class DeclarativeError(Exception):pass

class DeclarativeBase(DatabaseMixin):
    __model__             = None

    # field overrides
    __field_order__        = None
    __hidden_fields__      = None
    __disabled_fields__    = None
    __omitted_fields__     = None
    __additional_fields__  = None
    __limit_fields__       = None
    __field_attrs__        = None
    __field_widgets__      = None
    __field_widget_types__ = None

    #object overrides
    __base_widget_type__       = None
    __view_config_type__       = ViewConfig
    __widget_selector_type__   = None
    __metadata_type__          = None

    def _init_attrs(self):
        if self.__model__ is None:
            raise DeclarativeError('You must specify a __model__ for this form')
        if self.__hidden_fields__ is None:
            self.__hidden_fields__ = []
        if self.__disabled_fields__ is None:
            self.__disabled_fields__ = []
        if self.__omitted_fields__ is None:
            self.__omitted_fields__ = []
        if self.__limit_fields__ is None:
            self.__limit_fields__ = []
        if self.__field_widgets__ is None:
            self.__field_widgets__ = {}
        if self.__additional_fields__ is None:
            self.__additional_fields__ = {}
        if self.__field_attrs__ is None:
            self.__field_attrs__ = {}
        if self.__field_widgets__ is None:
            self.__field_widgets__ = {}
        if self.__field_widget_types__ is None:
            self.__field_widget_types__ = {}

        for attr in dir(self):
            if not attr.startswith('__'):
                value = getattr(self, attr)
                if isinstance(value, Widget):
                    self.__additional_fields__[attr] = value
                try:
                    if issubclass(value, Widget):
                        self.__field_widget_types__[attr] = value
                except TypeError:
                    pass

#        if 'widget' not in dir(self):
#            self.widget = self.__widget__

    @property
    def __widget__(self):
        if not hasattr(self, '___widget__'):
            self._init_attrs()
            self.___widget__ = ViewFactory().create(self.__view_config__).widget
        return self.___widget__

    def _do_apply_custom_view_config_options(self, view_config):
        return view_config

    def _append_list_attributes(self, view_config, attrs):
        for attr in attrs:
            type_ = getattr(self, '__'+attr+'__')
            fields = getattr(view_config, attr)
            for field in type_:
                if field not in fields:
                    fields.append(field)
        return view_config

    @property
    def __view_config__(self):
        if not hasattr(self, '___view_config__'):
            model      = self.__model__
            helper     = self._get_helper(model)
            metadata   = helper.get_metadata(model)
            identifier = helper.get_identifier(model)
            provider   = helper.get_provider(model)

            view_config = self.__view_config_type__(provider, identifier)

            attrs = ['disabled_fields', 'hidden_fields', 'omitted_fields']
            view_config = self._append_list_attributes(view_config, attrs)

            if self.__limit_fields__:
                view_config.limit_fields = self.__limit_fields__
            if self.__base_widget_type__:
                view_config.widget_type = self.__base_widget_type__
            if self.__field_order__:
                view_config.field_order = self.__field_order__
            if self.__widget_selector_type__:
                view_config.widget_selector = self.__widget_selector_type__
            if self.__metadata_type__:
                view_config.metadata_type = self.__metadata_type__

            view_config.field_widgets.update(self.__field_widgets__)
            view_config.additional_fields.update(self.__additional_fields__)
            view_config.field_widget_types.update(self.__field_widget_types__)
            view_config.field_attrs.update(self.__field_attrs__)

            view_config = self._do_apply_custom_view_config_options(view_config)

            self.___view_config__ = view_config

        return self.___view_config__

    def __call__(self, *args, **kw):
        return self.__widget__(*args, **kw)

class FormBase(DeclarativeBase):
    __action__            = None
    __required_fields__   = None
    __validators__        = None
    __base_validator__    = None
    __check_if_unique__   = False
    __view_config_type__  = EditableRecordViewConfig

    def _init_attrs(self):
        super(FormBase, self)._init_attrs()
        if self.__required_fields__ is None:
            self.__required_fields__ = []
        if self.__validators__ is None:
            self.__validators__ = {}

        for attr in dir(self):
            if not attr.startswith('__'):
                value = getattr(self, attr)
                if isinstance(value, Validator) or isinstance(value, type) and issubclass(value, Validator):
                    self.__validators__[attr] = value

    def _do_apply_custom_view_config_options(self, view_config):

        attrs = ['required_fields']
        view_config = self._append_list_attributes(view_config, attrs)

        if self.__base_validator__ is not None:
            view_config.widget_validator = self.__base_validator__
        view_config.check_if_unique = self.__check_if_unique__
        view_config.field_validators.update(self.__validators__)
        view_config._action = self.__action__

        return view_config

class TableBase(DeclarativeBase):
    __view_config_type__ = TableViewConfig
    __make_links__ = None

    def _do_apply_custom_view_config_options(self, view_config):
        super(TableBase, self)._init_attrs()
        if self.__make_links__ is not None:
            type_ = type(view_config)
            method = new.instancemethod(self.__make_links__, view_config, type_)
            view_config._make_links = method
        return view_config

class RecordBase(DeclarativeBase):
    __view_config_type__ = RecordViewConfig

class DatabaseBase(DeclarativeBase):
    __view_config_type__ = DatabaseViewConfig

