from nose.tools import eq_
from dbsprockets.test.model import *
from dbsprockets.test.base import setupDatabase, session, setupRecords, DBSprocketsTest
from tw.forms.fields import PasswordField
from tw.forms import Form
from formencode.validators import FieldsMatch
from formencode import Schema
from nose.tools import raises, eq_
from difflib import ndiff

from dbsprockets.declaratives import FormBase

session = None
engine  = None
connection = None
trans = None
def setup():
    global session, engine, connection, trans
    session, engine, connection = setupDatabase()
    import dbsprockets.primitives as p
    p.SAORMDBHelper = p._SAORMDBHelper()

class TestFormBase:

    def test_simple(self):
        class SimpleForm(FormBase):
            __model__ = User

        simple_form = SimpleForm()
        rendered = simple_form()
        assert rendered== """<form xmlns="http://www.w3.org/1999/xhtml" id="EditableRecordViewConfig_tg_user" method="post" class="dbsprocketstableform required">
    <div>
            <input type="hidden" name="user_id" class="hiddenfield" id="EditableRecordViewConfig_tg_user_user_id" value="" />
            <input type="hidden" name="table_name" class="hiddenfield" id="EditableRecordViewConfig_tg_user_table_name" value="" />
            <input type="hidden" name="dbsprockets_id" class="hiddenfield" id="EditableRecordViewConfig_tg_user_dbsprockets_id" value="" />
    </div>
    <table border="0" cellspacing="0" cellpadding="2">
        <tr class="even">
            <th>
                <label id="EditableRecordViewConfig_tg_user_user_id.label" for="EditableRecordViewConfig_tg_user_user_id" class="fieldlabel">User Id</label>
            </th>
            <td>
                <input type="text" name="user_id" class="textfield" id="EditableRecordViewConfig_tg_user_user_id" value="" disabled="disabled" />
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
                <label id="EditableRecordViewConfig_tg_user_email_address.label" for="EditableRecordViewConfig_tg_user_email_address" class="fieldlabel">Email Address</label>
            </th>
            <td>
                <textarea id="EditableRecordViewConfig_tg_user_email_address" name="email_address" class="textarea" rows="7" cols="50"></textarea>
            </td>
        </tr><tr class="odd">
            <th>
                <label id="EditableRecordViewConfig_tg_user_display_name.label" for="EditableRecordViewConfig_tg_user_display_name" class="fieldlabel">Display Name</label>
            </th>
            <td>
                <textarea id="EditableRecordViewConfig_tg_user_display_name" name="display_name" class="textarea" rows="7" cols="50"></textarea>
            </td>
        </tr><tr class="even">
            <th>
                <label id="EditableRecordViewConfig_tg_user_password.label" for="EditableRecordViewConfig_tg_user_password" class="fieldlabel">Password</label>
            </th>
            <td>
                <input type="password" name="password" class="passwordfield" id="EditableRecordViewConfig_tg_user_password" value="" />
            </td>
        </tr><tr class="odd">
            <th>
                <label id="EditableRecordViewConfig_tg_user_town.label" for="EditableRecordViewConfig_tg_user_town" class="fieldlabel">Town</label>
            </th>
            <td>
                <select name="town" class="foreignkeysingleselectfield" id="EditableRecordViewConfig_tg_user_town">
        <option value="" selected="selected">-----------</option>
</select>
            </td>
        </tr><tr class="even">
            <th>
                <label id="EditableRecordViewConfig_tg_user_created.label" for="EditableRecordViewConfig_tg_user_created" class="fieldlabel">Created</label>
            </th>
            <td>
                <div>
    <input type="text" id="EditableRecordViewConfig_tg_user_created" class="dbsprocketscalendardatetimepicker" name="created" value="2008-12-11 23:45:36" />
    <input type="button" id="EditableRecordViewConfig_tg_user_created_trigger" class="date_field_button" value="Choose" />
</div>
            </td>
        </tr><tr class="odd">
            <th>
                <label id="EditableRecordViewConfig_tg_user_many_many_tg_group.label" for="EditableRecordViewConfig_tg_user_many_many_tg_group" class="fieldlabel">tg_groups</label>
            </th>
            <td>
                <select name="many_many_tg_group" class="foreignkeymultipleselectfield" id="EditableRecordViewConfig_tg_user_many_many_tg_group" multiple="multiple" size="5">
</select>
            </td>
        </tr><tr class="even">
            <th>
            </th>
            <td>
                <input type="submit" class="submitbutton" id="EditableRecordViewConfig_tg_user_submit" value="Submit" />
            </td>
        </tr>
    </table>
</form>""", rendered
