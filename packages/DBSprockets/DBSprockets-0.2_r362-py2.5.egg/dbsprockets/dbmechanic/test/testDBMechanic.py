import os
from routes import url_for
from dbsprockets.test.base import *
from dbsprockets.test.model import *
from dbsprockets.dbmechanic.dbmechanic import DBMechanic
from sqlalchemy.orm import sessionmaker, scoped_session
from dbsprockets.saprovider import SAProvider

#from dbsprockets.dbmechanic.test.middleware import make_app

config = os.path.dirname(os.path.abspath(__file__))+os.sep+'test.ini'
global_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

"""
class TestCommentsController:
    def __init__(self, *args, **kw):
        global_dict = dict(PATH=global_path)
        self.app = make_app(global_dict, config)

    def test_index(self):
        #print url_for(controller='comments')
        response = self.app.get('/')
        assert response == 'asdf', response
        # Test response...

"""
engine = create_engine('sqlite://')
metadata.bind = engine
metadata.create_all(bind=engine)
Session = sessionmaker(bind=engine, autoflush=True, transactional=True)
session = Session()

u = User()
u.user_name=u'asdf'
u.password = u'asdf'
u.email=u"asdf@asdf.com"
session.save(u)
g = Group(group_name=u"group", display_name=u"group")
session.save(g)
session.flush()

def setup():
    setupDatabase()

class _testDBMechanic:
    def setup(self):
        provider = SAProvider(metadata)
        self.dbmechanic = DBMechanic(provider, '/dbmechanic')
        
    def testCreateObj(self):
        pass
    
    def testDatabaseView(self):
        d = self.dbmechanic.index()
        view = d['databaseView']
        value = d['databaseValue']
        
        s = view.display(value=value)
        assert """<div class="tablelabelwidget">
<a href="/dbmechanic/tableView/tg_user">tg_user</a>
</div>
<div class="tablelabelwidget">
<a href="/dbmechanic/tableView/town_table">town_table</a>
</div>
<input type="hidden" name="dbsprockets_id" class="hiddenfield" id="databaseView_dbsprockets_id" />
</div>""" in s, "actual: %s"%s
    
    def testTableDef(self):
        d = self.dbmechanic.tableDef(tableName='test_table')
        view = d['mainView']
        #value = d['mainValue']
        value = view.display(value={})
        assert """<tr class="tabledefwidget">
    <td>
        Password
    </td>
    <td>
    String(length=20, convert_unicode=False, assert_unicode=None)
    </td>
</tr>
<input type="hidden" name="dbsprockets_id" class="hiddenfield" id="tableDef__test_table_dbsprockets_id" />
</table>""" in value, value
        
    def testTableView(self):
        
        u = User()
        u.user_name=u'user2'
        u.password = u'asdf'
        u.email=u"asdf@asdf.com"
        session.save(u)
        g = Group(group_name=u"table_view_group", display_name=u"group")
        session.save(g)
        session.flush()
        
        d = self.dbmechanic.tableView(tableName='tg_user')
        view = d['mainView']
        value = d['mainValue']
        value = view.display(value=value)
        assert """a href="/dbmechanic/editRecord/tg_user?user_id=1">edit</a>|<a href="/dbmechanic/delete/tg_user?user_id=1">delete</a></td><td>1</td><td>asdf</td><td></td><td></td><td>******</td><td>""" in value, value
        
    def testAddRecord(self):
        d = self.dbmechanic.addRecord(tableName='tg_user')
        view = d['mainView']
        value = d['mainValue']
        value = view.display(value=value)
        assert """<td>
                <div>
    <input type="text" id="addRecord__tg_user_created" class="dbsprocketscalendardatetimepicker" name="created" value="2007-12-21 19:02:25" />
    <input type="button" id="addRecord__tg_user_created_trigger" class="date_field_button" value="Choose" />
</div>
            </td>
        </tr><tr class="even">
            <th>
            </th>
            <td>
                <input type="submit" class="submitbutton" id="addRecord__tg_user_submit" value="Submit" />
            </td>
        </tr>
    </table>"""
        
    def testEditRecord(self):
        d = self.dbmechanic.editRecord(tableName='tg_user', user_id=1)
        view = d['mainView']
        value = d['mainValue']
        value = view.display(value=value)
        assert """<td>
                <div>
    <input type="text" id="editRecord__tg_user_created" class="dbsprocketscalendardatetimepicker" name="created" value="2007-12-21 20:45:00" />
    <input type="button" id="editRecord__tg_user_created_trigger" class="date_field_button" value="Choose" />
</div>
            </td>
        </tr><tr class="even">
            <th>
            </th>
            <td>
                <input type="submit" class="submitbutton" id="editRecord__tg_user_submit" value="Submit" />
            </td>
        </tr>
    </table>
</form>"""

#cant test this until we can do it properly through paste
#    def testAdd(self):
#        d = self.dbmechanic.add(tableName='tg_user', user_name='asdf2')
#        assert d == {}, "%s"%d
