from dbsprockets.primitives import *
from dbsprockets.test.model import *
from dbsprockets.test.base import setupDatabase, session, setupRecords, DBSprocketsTest
from tw.forms.fields import PasswordField
from tw.forms import Form
from formencode.validators import FieldsMatch
from formencode import Schema
from nose.tools import raises, eq_
from difflib import ndiff

session = None
engine  = None
connection = None
trans = None
def setup():
    global session, engine, connection, trans
    session, engine, connection = setupDatabase()
    import dbsprockets.primitives as p
    p.generator = SprocketGenerator()
    p.fetcher = DataFetcher()
    p.make_form = p.generator.make_form
    p.make_table = p.generator.make_table
    p.get_table_value = p.fetcher.get_table_value
    p.SAORMDBHelper = p._SAORMDBHelper()
    global make_form, make_table, get_table_value
    make_form = p.make_form
    make_table = p.make_table
    get_table_value = p.get_table_value

class TestDBHelper:

    def setup(self):
        self.helper = DBHelper()

    @raises(NotImplementedError)
    def testGetMetadata(self):
        self.helper.get_metadata(None)

    @raises(NotImplementedError)
    def testGetIdentifier(self):
        self.helper.get_identifier(None)

    @raises(NotImplementedError)
    def testValidateModel(self):
        self.helper.validate_model(None)

class TestSAORMHelper:

    def setup(self):
        self.helper = SAORMDBHelper

    @raises(TypeError)
    def testValidateModelBad(self):
        self.helper.validate_model(None)

    @raises(Exception)
    def testValidateModelBadNoFields(self):
        class Dummy:
            c = {}

        self.helper.validate_model(Dummy)

class TestDatabaseMixin:

    def setup(self):
        self.mixin = DatabaseMixin()

    def test_create(self):
        pass

    @raises(Exception)
    def test_get_helperBad(self):
        self.mixin._get_helper(None)


@raises(Exception)
def _create(model,
             action,
             identifier='',
             controller='',
             hidden_fields=[],
             disabled_fields=[],
             required_fields=[],
             omitted_fields=[],
             additional_fields=[],
             limit_fields=None,
             field_attrs={},
             widgets={},
             validators={},
             form_validator=None,
             check_if_unique=True):
    make_form(model=model,
             action=action,
             identifier=identifier,
             controller=controller,
             hidden_fields=hidden_fields,
             disabled_fields=disabled_fields,
             required_fields=reduce,
             omitted_fields=omitted_fields,
             additional_fields=additional_fields,
             limit_fields=limit_fields,
             field_attrs=field_attrs,
             widgets=widgets,
             validators=validators,
             form_validator=form_validator,
             check_if_unique=check_if_unique)


class TestPrimitives(DBSprocketsTest):

    def test_make_form_bad(self):
        badInput = ('a', (), [], 1, 1.2, False, {}, None)
        for input in badInput[1:]:
            yield _create, User, input
        for input in badInput[1:]:
            yield _create, User, 'a', input
        for input in badInput[1:]:
            yield _create, User, 'a', 'a', input
        badInput = ('a', 1, 1.2, False, {}, None)
        for input in badInput:
            yield _create, User, 'a', 'a', 'a', input
        for input in badInput:
            yield _create, User, 'a', 'a', 'a', [], input
        for input in badInput:
            yield _create, User, 'a', 'a', 'a', [], [], input
        for input in badInput:
            yield _create, User, 'a', 'a', 'a', [], [], [], input
        badInput = ('a', 1, 1.2, False, (),)
        for input in badInput:
            yield _create, User, 'a', 'a', 'a', [], [], [], [], input

        badInput = ('a', 1, 1.2, False, None)
        for input in badInput:
            yield _create, User, 'a', 'a', 'a', [], [], [], [], [], input

        badInput = ('a', 1, 1.2, False, (), [], None)
        for input in badInput:
            yield _create, User, 'a', 'a', 'a', [], [], [], [], [], None, input
        badInput = ('a', 1, 1.2, False, (), [],)
        for input in badInput:
            yield _create, User, 'a', 'a', 'a', [], [], [], [], [], None, {}, input
        for input in badInput:
            yield _create, User, 'a', 'a', 'a', [], [], [], [], [], None, {}, {}, input
        for input in badInput:
            yield _create, User, 'a', 'a', 'a', [], [], [], [], [], None, {}, {}, {}, input
        badInput = ('a', 1, 1.2, (), [], {},)
        for input in badInput:
            yield _create, User, 'a', 'a', 'a', [], [], [], [], [], None, {}, {}, {}, None, input

    def test_make_form(self):
        form = make_form(User, 'add')
        rendered = form()
        assert rendered.endswith("""</tr><tr class="even">
            <th>
            </th>
            <td>
                <input type="submit" class="submitbutton" id="EditableRecordViewConfig_tg_user_submit" value="Submit" />
            </td>
        </tr>
    </table>
</form>"""), rendered

    def test_make_form_with_hidden_fields(self):
        form = make_form(User, 'add', hidden_fields=['email_address', 'tg_groups', 'town', 'password', 'display_name'])
        rendered = form()
        assert """<form xmlns="http://www.w3.org/1999/xhtml" id="EditableRecordViewConfig_tg_user" action="add" method="post" class="dbsprocketstableform required">
    <div>
            <input type="hidden" name="user_id" class="hiddenfield" id="EditableRecordViewConfig_tg_user_user_id" value="" />
            <input type="hidden" name="email_address" class="hiddenfield" id="EditableRecordViewConfig_tg_user_email_address" value="" />
            <input type="hidden" name="display_name" class="hiddenfield" id="EditableRecordViewConfig_tg_user_display_name" value="" />
            <input type="hidden" name="password" class="hiddenfield" id="EditableRecordViewConfig_tg_user_password" value="" />
            <input type="hidden" name="town" class="hiddenfield" id="EditableRecordViewConfig_tg_user_town" value="" />
            <input type="hidden" name="table_name" class="hiddenfield" id="EditableRecordViewConfig_tg_user_table_name" value="" />
            <input type="hidden" name="tg_groups" class="hiddenfield" id="EditableRecordViewConfig_tg_user_tg_groups" value="" />
            <input type="hidden" name="dbsprockets_id" class="hiddenfield" id="EditableRecordViewConfig_tg_user_dbsprockets_id" value="" />
    </div>""" in rendered, rendered

    def test_make_form_with_limit_fields(self):
        form = make_form(User, 'add', limit_fields=['user_name', 'password'])
        actual = form()
        expected = """<form xmlns="http://www.w3.org/1999/xhtml" id="EditableRecordViewConfig_tg_user" action="add" method="post" class="dbsprocketstableform required">
    <div>
            <input type="hidden" name="table_name" class="hiddenfield" id="EditableRecordViewConfig_tg_user_table_name" value="" />
            <input type="hidden" name="dbsprockets_id" class="hiddenfield" id="EditableRecordViewConfig_tg_user_dbsprockets_id" value="" />
    </div>
    <table border="0" cellspacing="0" cellpadding="2">
        <tr class="even">
            <th>
                <label id="EditableRecordViewConfig_tg_user_user_name.label" for="EditableRecordViewConfig_tg_user_user_name" class="fieldlabel">User Name</label>
            </th>
            <td>
                <input type="text" name="user_name" class="textfield" id="EditableRecordViewConfig_tg_user_user_name" value="" maxlength="16" size="16" />
            </td>
        </tr><tr class="odd">
            <th>
                <label id="EditableRecordViewConfig_tg_user_password.label" for="EditableRecordViewConfig_tg_user_password" class="fieldlabel">Password</label>
            </th>
            <td>
                <input type="password" name="password" class="passwordfield" id="EditableRecordViewConfig_tg_user_password" value="" />
            </td>
        </tr><tr class="even">
            <th>
            </th>
            <td>
                <input type="submit" class="submitbutton" id="EditableRecordViewConfig_tg_user_submit" value="Submit" />
            </td>
        </tr>
    </table>
</form>"""
        assert actual == expected, ''.join(a for a in ndiff(expected.splitlines(1), actual.splitlines(1)))

    def test_make_form_with_omitted_fields(self):
        form = make_form(User, 'add', omitted_fields=['email_address', 'tg_groups', 'town', 'password', 'display_name'])
        rendered = form()
        assert 'password' not in rendered, rendered

    def test_make_form_with_widget_type(self):
        form = make_form(User, 'add', omitted_fields=['email_address', 'tg_groups', 'town', 'password', 'display_name'], form_widget_type=Form)
        rendered = form()
        assert """<form xmlns="http://www.w3.org/1999/xhtml" id="EditableRecordViewConfig_tg_user" action="add" method="post" class="required form">
    <div>""" in rendered, rendered

    def test_make_form_with_additional_field(self):
        form = make_form(User, 'add', omitted_fields=['email_address', 'tg_groups', 'town', 'password', 'display_name'])
        rendered = form()
        assert 'password' not in rendered, rendered

    def test_make_form_with_disabled_field(self):
        form = make_form(User, 'add', disabled_fields=['user_id',])
        rendered = form()
        assert """</th>
            <td>
                <input type="text" name="user_id" class="textfield" id="EditableRecordViewConfig_tg_user_user_id" value="" disabled="disabled" />
            </td>
        </tr><tr class="odd">
            <th>""" in rendered, rendered

    def test_make_form_ultimate_use_case(self):
        required_fields = ['user_name',]
        omitted_fields  = ['enabled', 'user_id', 'tg_groups', 'created', 'town', 'password', 'email_address', 'display_name']
        additional_fields = {'password_verification':PasswordField('password_verification', label_text='Verify'),}
        form_validator =  Schema(chained_validators=(FieldsMatch('password',
                                                                'password_verification',
                                                                messages={'invalidNoMatch':
                                                                          "Passwords do not match"}),))

        form = make_form(User, 'add',
                        required_fields=required_fields,
                        omitted_fields=omitted_fields,
                        additional_fields=additional_fields,
                        form_validator=form_validator)

        actual = form()
        expected =  """<form xmlns="http://www.w3.org/1999/xhtml" id="EditableRecordViewConfig_tg_user" action="add" method="post" class="dbsprocketstableform required">
    <div>
            <input type="hidden" name="table_name" class="hiddenfield" id="EditableRecordViewConfig_tg_user_table_name" value="" />
            <input type="hidden" name="dbsprockets_id" class="hiddenfield" id="EditableRecordViewConfig_tg_user_dbsprockets_id" value="" />
    </div>
    <table border="0" cellspacing="0" cellpadding="2">
        <tr class="even">
            <th>
                <label id="EditableRecordViewConfig_tg_user_user_name.label" for="EditableRecordViewConfig_tg_user_user_name" class="fieldlabel">User Name</label>
            </th>
            <td>
                <input type="text" name="user_name" class="textfield" id="EditableRecordViewConfig_tg_user_user_name" value="" maxlength="16" size="16" />
            </td>
        </tr><tr class="odd">
            <th>
                <label id="EditableRecordViewConfig_tg_user_password_verification.label" for="EditableRecordViewConfig_tg_user_password_verification" class="fieldlabel">Verify</label>
            </th>
            <td>
                <input type="password" name="password_verification" class="passwordfield" id="EditableRecordViewConfig_tg_user_password_verification" value="" />
            </td>
        </tr><tr class="even">
            <th>
            </th>
            <td>
                <input type="submit" class="submitbutton" id="EditableRecordViewConfig_tg_user_submit" value="Submit" />
            </td>
        </tr>
    </table>
</form>"""
        assert actual == expected, ''.join(a for a in ndiff(expected.splitlines(1), actual.splitlines(1)))

    def test_make_form_hidden_id(self):
        # this addresses issue74"""
        form = make_form(User, '', hidden_fields=['user_id',])
        actual = form()
        assert """<form xmlns="http://www.w3.org/1999/xhtml" id="EditableRecordViewConfig_tg_user" action="" method="post" class="dbsprocketstableform required">
    <div>
            <input type="hidden" name="user_id" class="hiddenfield" id="EditableRecordViewConfig_tg_user_user_id" value="" />
            <input type="hidden" name="table_name" class="hiddenfield" id="EditableRecordViewConfig_tg_user_table_name" value="" />
            <input type="hidden" name="dbsprockets_id" class="hiddenfield" id="EditableRecordViewConfig_tg_user_dbsprockets_id" value="" />
    </div>
    <table border="0" cellspacing="0" cellpadding="2">
        <tr class="even">
            <th>
                <label id="EditableRecordViewConfig_tg_user_user_name.label" for="EditableRecordViewConfig_tg_user_user_name" class="fieldlabel">User Name</label>
            </th>
            <td>
                <input type="text" name="user_name" class="textfield" id="EditableRecordViewConfig_tg_user_user_name" value="" maxlength="16" size="16" />
            </td>
        </tr><tr class="odd">
            <th>
                <label id="EditableRecordViewConfig_tg_user_email_address.label" for="EditableRecordViewConfig_tg_user_email_address" class="fieldlabel">Email Address</label>
            </th>
            <td>
                <textarea id="EditableRecordViewConfig_tg_user_email_address" name="email_address" class="textarea" rows="7" cols="50"></textarea>
            </td>""" in actual, actual

    def test_make_form_field_order(self):
        #issue 35
        form = make_form(User, '', field_order=['password', 'user_name'], limit_fields=['user_name', 'password'])
        actual = form()
        expected="""<form xmlns="http://www.w3.org/1999/xhtml" id="EditableRecordViewConfig_tg_user" action="" method="post" class="dbsprocketstableform required">
    <div>
            <input type="hidden" name="table_name" class="hiddenfield" id="EditableRecordViewConfig_tg_user_table_name" value="" />
            <input type="hidden" name="dbsprockets_id" class="hiddenfield" id="EditableRecordViewConfig_tg_user_dbsprockets_id" value="" />
    </div>
    <table border="0" cellspacing="0" cellpadding="2">
        <tr class="even">
            <th>
                <label id="EditableRecordViewConfig_tg_user_password.label" for="EditableRecordViewConfig_tg_user_password" class="fieldlabel">Password</label>
            </th>
            <td>
                <input type="password" name="password" class="passwordfield" id="EditableRecordViewConfig_tg_user_password" value="" />
            </td>
        </tr><tr class="odd">
            <th>
                <label id="EditableRecordViewConfig_tg_user_user_name.label" for="EditableRecordViewConfig_tg_user_user_name" class="fieldlabel">User Name</label>
            </th>
            <td>
                <input type="text" name="user_name" class="textfield" id="EditableRecordViewConfig_tg_user_user_name" value="" maxlength="16" size="16" />
            </td>
        </tr><tr class="even">
            <th>
            </th>
            <td>
                <input type="submit" class="submitbutton" id="EditableRecordViewConfig_tg_user_submit" value="Submit" />
            </td>
        </tr>
    </table>
</form>"""
        assert expected== actual, ''.join(a for a in ndiff(expected.splitlines(1), actual.splitlines(1)))



    #this test is conflicting with the dbmechanic tests
    def test_make_table_with_data(self):
        actual = get_table_value(User)
        table = make_table(User, '/')
        rendered = table(value=actual)
        assert """<table xmlns="http://www.w3.org/1999/xhtml" id="TableViewConfig_tg_user" class="grid" cellpadding="0" cellspacing="1" border="0">
    <thead>
        <tr>
            <th class="col_0">
            </th><th class="col_1">
            user_id
            </th><th class="col_2">
            user_name
            </th><th class="col_3">
            email_address
            </th><th class="col_4">
            display_name
            </th><th class="col_5">
            password
            </th><th class="col_6">
            town
            </th><th class="col_7">
            created
            </th><th class="col_8">
            tg_groups
            </th>
        </tr>
    </thead>
    <tbody>
        <tr class="even">
            <td><a href="//editRecord/tg_user?user_id=""" in rendered, rendered

    def testMakeTableWithDataAndNoController(self):
        actual = get_table_value(User)
        table = make_table(User)
        rendered = table(value=actual)
        assert """<table xmlns="http://www.w3.org/1999/xhtml" id="TableViewConfig_tg_user" class="grid" cellpadding="0" cellspacing="1" border="0">
    <thead>
        <tr>
            <th class="col_0">
            user_id
            </th><th class="col_1">
            user_name
            </th><th class="col_2">
            email_address
            </th><th class="col_3">
            display_name
            </th><th class="col_4">
            password
            </th><th class="col_5">
            town
            </th><th class="col_6">
            created
            </th><th class="col_7">
            tg_groups
            </th>
        </tr>
    </thead>
    <tbody>
        <tr class="even">
            <td>""" in rendered, rendered

    #this test is conflicting with the dbmechanic tests
    def test_get_table_value(self):
        actual = get_table_value(User)
        expected = [{u'town': u'Arvada',
          u'email_address': None, u'display_name': None, u'password': '******', u'user_name': u'asdf'}]
        for i, item in enumerate(expected):
            for key, value in item.iteritems():
                assert actual[i][key] == value, "%s failed on key: %s"%(actual[i], key)

    #this test is conflicting with the dbmechanic tests
    def test_make_record_value(self):
        actual = make_record_view(User)
        value = {u'town': u'Arvada', u'user_id': 1,
          u'email_address': None, u'display_name': None, u'password': '******', u'user_name': u'asdf', 'created':None}
        actual = actual.render(value)
        expected = """<table xmlns="http://www.w3.org/1999/xhtml" id="RecordViewConfig_tg_user" class="recordviewwidget">
<tr><th>Name</th><th>Value</th></tr>
<tr class="recordfieldwidget">
    <td>
        <b>user_id</b>
    </td>
    <td> 1
    </td>
</tr>
<tr class="recordfieldwidget">
    <td>
        <b>user_name</b>
    </td>
    <td> asdf
    </td>
</tr>
<tr class="recordfieldwidget">
    <td>
        <b>email_address</b>
    </td>
    <td>
    </td>
</tr>
<tr class="recordfieldwidget">
    <td>
        <b>display_name</b>
    </td>
    <td>
    </td>
</tr>
<tr class="recordfieldwidget">
    <td>
        <b>password</b>
    </td>
    <td> ******
    </td>
</tr>
<tr class="recordfieldwidget">
    <td>
        <b>town</b>
    </td>
    <td> Arvada
    </td>
</tr>
<tr class="recordfieldwidget">
    <td>
        <b>created</b>
    </td>
    <td>
    </td>
</tr>
</table>"""
        assert actual == expected, ''.join(a for a in ndiff(expected.splitlines(1), actual.splitlines(1)))
    def testGetFormDefaults(self):
        actual = get_form_defaults(Example)
        assert sorted(actual.keys()) == ['Integer', 'created'], sorted(actual.keys())
        assert actual['Integer'] == 10

class TestSAORMDBHelperSAORMDBHelper:
    def setup(self):
        self.helper = SAORMDBHelper

    def testGetIdentifier(self):
        eq_(self.helper.get_identifier(User), 'tg_user')


