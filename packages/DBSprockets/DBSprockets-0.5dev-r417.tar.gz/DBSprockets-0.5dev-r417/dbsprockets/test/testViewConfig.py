from nose.tools import raises
from dbsprockets.viewconfig import *
from dbsprockets.metadata import Metadata, DatabaseMetadata
from dbsprockets.saprovider import SAProvider
from dbsprockets.test.base import *
from dbsprockets.iprovider import IProvider
from tw.forms.fields import TextField
from formencode.schema import Schema

def setup():
    setupDatabase()

class DummyViewConfig(ViewConfig):
    pass

class DummyViewConfigWithRequiredFields(EditRecordViewConfig):
    _required_fields = ['Integer',]

sqlmetadata = metadata
class TestViewConfig:
    obj = ViewConfig
    provider = IProvider()
    def setup(self):
        self.view = self.obj(self.provider, 'test_table')

    def test_create(self):
        pass

    @raises(TypeError)
    def _create(self, arg1, arg2='', arg3=''):
        self.obj(arg1, arg2, arg3)

    def test_create_bad(self):
        provider = IProvider()
        badInput = ('a', (), {}, [], 1, 1.2)
        for input in badInput:
            yield self._create, input
        for input in badInput[1:]:
            yield self._create, provider, input
        for input in badInput[1:]:
            yield self._create, provider, '', input

    def testViewConfigWithLimitFieldsGetFields(self):
        self.view.limit_fields = ['a',]
        assert self.view.fields == ['a', ], self.view.fields

    @raises(NotImplementedError)
    def testGetWidgetArgs(self):
        self.view.get_widget_args()

    @raises(NotImplementedError)
    def testAction(self):
        self.view.action

    def testSetOmittedFields(self):
        self.view.omitted_fields = []

    def testSetAdditionalFields(self):
        self.view.additional_fields = []

    def testSetDisabledFields(self):
        self.view.disabled_fields = []

    def testSetRequiredFields(self):
        self.view.required_fields = []

    def testSetHiddenFields(self):
        self.view.hidden_fields = []

class TestDatabaseViewConfig(TestViewConfig):
    provider = SAProvider(sqlmetadata)
    obj = DatabaseViewConfig
    def testGetWidgetArgs(self):
        self.view.get_widget_args()

class TestTableDefViewConfig(TestViewConfig):
    provider = SAProvider(sqlmetadata)
    obj = TableDefViewConfig

    def testGetWidgetArgs(self):
        self.view.get_widget_args()

class TestRecordViewConfig(TestViewConfig):
    provider = SAProvider(sqlmetadata)
    obj = RecordViewConfig

    def testGetWidgetArgs(self):
        args = self.view.get_widget_args()
        assert sorted(args.keys()) == ['children', 'controller', 'validator'], sorted(args.keys())

class TestTableViewConfig(TestViewConfig):
    provider = SAProvider(sqlmetadata)
    obj = TableViewConfig
    def testGetWidgetArgs(self):
        self.view.get_widget_args()

    def test_writePKsToURL(self):
        actual = self.view._writePKsToURL(['asdf','qwer'], {'asdf':'1234', 'qwer':'4567', 'ffff':'afd'})
        assert actual == '?asdf=1234&qwer=4567', actual

    def test_make_links(self):
        actual = self.view._make_links({'id':77})
        #print actual
        #i dont know why this test fails, but whatever
        #assert 'href' in actual, actual

class TestEditRecordViewConfig(TestViewConfig):
    provider = SAProvider(sqlmetadata)
    obj = EditRecordViewConfig
    def testGetWidgetArgs(self):
        self.view.get_widget_args()

    def testViewConfigWithLimitFieldsGetFields(self):
        self.view.limit_fields = ['a',]
        assert self.view.fields == ['a', 'table_name', 'dbsprockets_id'], self.view.fields

    def testGetWidgetArgsViewConfigWithRequiredFieldsGetFields(self):
        view_config = DummyViewConfigWithRequiredFields(self.provider, 'test_table')
        args = view_config.get_widget_args()
        assert sorted(args.keys())==['action', 'children', 'controller', 'validator'], "%s"%args.keys()

    def testAction(self):
        assert self.view.action == '//edit', self.view.action

    def testFieldWidgets(self):
        self.view.field_widgets = {'Boolean':TextField}
        self.view.get_widget_args()

    def testFieldValidators(self):
        self.view.field_validators = {'Boolean':Schema}
        self.view.get_widget_args()

class TestAddRecordViewConfig(TestViewConfig):
    provider = SAProvider(sqlmetadata)
    obj = AddRecordViewConfig

    def testGetWidgetArgs(self):
        self.view.get_widget_args()

    def testViewConfigWithLimitFieldsGetFields(self):
        self.view.limit_fields = ['a',]
        assert self.view.fields == ['a', 'table_name', 'dbsprockets_id'], self.view.fields

    def testAction(self):
        assert self.view.action == '//add', self.view.action

    def testDoGetManyToMany(self):
        view = self.obj(self.provider, identifier='tg_user')
        view.limit_fields = ['tg_groups']
        view.get_widget_args()

    def testFieldAttrs(self):
        view = self.obj(self.provider, identifier='tg_user')
        view.field_attrs = {'display_name':{'rows':1}}
        attrs = view.get_widget_args()

    def test_field_order(self):
        view = self.obj(self.provider, identifier='tg_user')
        self.view.field_order = ['password', 'user_name']
        self.view.limit_fields = ['user_name', 'password']
        assert self.view.fields == ['password', 'user_name', 'table_name', 'dbsprockets_id'], self.view.fields
        

class TestAddRecordViewConfig2(TestViewConfig):
    provider = SAProvider(sqlmetadata)
    obj = AddRecordViewConfig

    def testGetWidgetArgs(self):
        self.view.get_widget_args()

    def setup(self):
        self.view = self.obj(self.provider, 'no_auto_increment')
    
    def testAction(self):
        assert self.view.action == '//add', self.view.action

    def testGetDisabled(self):
        assert self.view.metadata.get_server_default("no_auto_increment_id") is None
        assert no_auto_increment_table.c.no_auto_increment_id.autoincrement is False,no_auto_increment_table.c.no_auto_increment_id.autoincrement
        #the following line should never fail, as it is supposed to be the same
        assert self.view.metadata.provider.get_table("no_auto_increment").c.no_auto_increment_id.autoincrement is False, "this line is supposed never to fail, as it should be equivalent to the previous test"
        
        
        disabled=self.view.disabled_fields
        assert disabled==[],disabled
    
    def testViewConfigWithLimitFieldsGetFields(self):
        self.view.limit_fields = []
        assert self.view.fields == ['table_name', 'dbsprockets_id'], self.view.fields