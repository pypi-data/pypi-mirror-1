from nose.tools import raises, eq_
from dbsprockets.saprovider import SAProvider
from dbsprockets.test.testIProvider import TestIProvider
from model import *
from cgi import FieldStorage
from dbsprockets.test.base import setupDatabase, sortedTableList, teardownDatabase, setupRecords, DBSprocketsTest
from cStringIO import StringIO

session = None
engine = None
connect = None
trans = None

def setup():
    global session, engine, connect, trans
    session, engine, connect = setupDatabase()
#    trans = engine.begin()

def teardown():
    global session, trans

class _TestSAProvider(DBSprocketsTest):
    def setup(self):
        super(_TestSAProvider, self).setup()
        self.provider = SAProvider(metadata)

    def test_create(self):
        pass

    @raises(TypeError)
    def _create(self, arg1):
        SAProvider(arg1)

    def _test_create_bad(self):
        badInput = (1, 1.2, u'a', None, (), [], {})
        for input in badInput:
            yield self._create, badInput

    def test_get_tables(self):
        tables = sorted(self.provider.get_tables())
        eq_(tables, sortedTableList)

    def testGetTable(self):
        table = self.provider.get_table('tg_user')
        eq_(table.name, 'tg_user')

    def testGetColumns(self):
        columns = sorted(self.provider.get_columns('tg_user'))
        eq_(columns, ['created', 'display_name', 'email_address', 'password', 'town', 'user_id', 'user_name'])

    def testGetColumn(self):
        column = self.provider.get_column('tg_user', 'user_id')
        eq_(column.name, 'user_id')

    def testGetPrimaryKeys(self):
        keys = self.provider.get_primary_keys('tg_user')
        eq_(keys, ['user_id'])

    def testSelectOnPks(self):
        rows = self.provider.select_on_primary_keys('tg_user', dict(user_id=self.user.user_id))
        actual = (rows[0])[:-2]
        assert list(actual) == [self.user.user_id, u'asdf', None, None, 'asdf'], "%s"%list(actual)

    def testSelectOnPksWithColumnsLimit(self):
        rows = self.provider.select_on_primary_keys('tg_user', dict(user_id=self.user.user_id), columns_limit=['user_name'])
        actual = rows[0]
        assert list(actual) == [u'asdf', ], "%s"%list(actual)

    def test_select_with_limit_and_offset(self):
        rows = self.provider.select('tg_group', dict(user_id=1), columns_limit=['group_name'], result_limit=2, result_offset=2)
        actual = rows
        assert list(actual) == [(u'2',), (u'3',), ], "%s"%list(actual)

    def testSelect(self):
        rows = self.provider.select('tg_user')
        actual = (rows[0])[:-2]
        assert list(actual) == [self.user.user_id, u'asdf', None, None, 'asdf'], "%s"%list(actual)

    def testSelectWithColumnsLimit(self):
        rows = self.provider.select('tg_user', columns_limit=['user_name'])
        actual = rows[0]
        assert list(actual) == [u'asdf'], "%s"%list(actual)

    def testSelectEmpty(self):
        rows = self.provider.select('tg_user', values=dict(user_name=u'asdf', user_id=0))
        assert rows == [], "%s"%rows

    def test_add(self):
        self.provider.add('tg_user', values=dict(user_name=u'asdf2', user_id=0))

    def test_add_with_columns_limit(self):
        self.provider.add('tg_user', values=dict(user_name=u'asdf4', user_id=0, enabled=True), columns_limit=['user_name', 'user_id'])

    def _test_delete(self):
        self.provider.delete('tg_user', dict(user_id=self.user.user_id))

    def test_edit(self):
        self.provider.edit('tg_user', values=dict(user_id=0, user_name=u'asdf2'))
        rows = users_table.select(users_table.c.user_name==u'asdf').execute().fetchall()
        assert len(rows) == 1
        row = rows[0][:-2]
        assert row == (self.user.user_id, u'asdf', None, None, u'asdf'), "%s"%row

    def testGetViewColumnName(self):
        actual = self.provider.get_view_column_name('town_table')
        assert actual == 'name', actual

    def testGetIDColumnName(self):
        actual = self.provider.get_id_column_name('town_table')
        assert actual == 'town_id', actual

    def testGetForeignKeys(self):
        actual = self.provider.get_foreign_keys('tg_user')
        c = users_table.columns['town']
        assert actual == [c, ], actual

    def testGetAssociatedManyToManyTables(self):
        actual = self.provider.get_associated_many_to_many_tables('tg_user')
        assert actual == ['tg_group', ], actual

    def testGetManyToManyColumns2(self):
        actual = sorted(self.provider.get_many_to_many_columns('tg_group'))
        eq_(actual,  [u'permissions', u'tg_users'])

    def testGetManyToManyColumns(self):
        actual = self.provider.get_many_to_many_columns('tg_user')
        eq_(actual,   [u'tg_groups'])

    def testGetManyToManyTables(self):
        actual = sorted(self.provider.get_many_to_many_tables())
        assert actual == ['group_permission', 'user_group'], "%s"%actual

    def testSetManyToMany(self):
        groups = groups_table.select().limit(2).execute().fetchall()
        group1_id = groups[0].group_id
        group2_id = groups[1].group_id
        user_id = self.user.user_id
        user_group_table.delete().execute()
        self.provider.set_many_to_many('tg_user', self.user.user_id, 'tg_group', [group1_id, group2_id])
        rows = user_group_table.select().execute().fetchall()
        assert rows == [(user_id, group1_id), (user_id, group2_id)], "%s"%rows

    def testSetManyToManyToo(self):
        group = self.user.groups[0]
        user_group_table.delete().execute()
        self.provider.set_many_to_many('tg_group', group.group_id, 'tg_user', [self.user.user_id,])
        rows = user_group_table.select().execute().fetchall()
        assert rows == [(self.user.user_id, group.group_id),], "%s"%rows

    def _testSetManyToManyFailsafe(self):
        r = self.provider.set_many_to_many('tg_group', 1, 'test_table', [1,])
        eq_(r, None)

    def test_get_foreign_key_dict(self):
        d = self.provider.get_foreign_key_dict('tg_user')
        assert d.keys() == ['town']
        assert set(d['town'].values()) == set([u'Arvada', u'Denver', u'Golden', u'Boulder']), d['town'].values()
 #       if engine.url.drivername == 'postgres':
        #this works in postgres because postgres does weird things with ids
#            assert d == {'town': {17: u'Arvada', 18: u'Denver', 19: u'Golden', 20: u'Boulder'}},  "%s"%d

    def test_find_first_columnColumnNotFound(self):
        actual = self.provider._find_first_column('test_table', ['not_possible',])
        eq_(actual, 'id')

    def testIsUniqueNotUnique(self):
        actual = self.provider.is_unique(users_table.c.user_name, u'asdf')
        assert not actual

    def testIsUnique(self):
        actual = self.provider.is_unique(users_table.c.user_name, u'asdf_q2341234')
        assert actual

    def _test_add_field_storage(self):
        self.provider.add('test_table', values=dict(BLOB=FieldStorage('asdf.txt', StringIO())))

    def testGetDefaultValues(self):
        #we dont want to check this for reflected tables (there are no defaults set):
        if 'Reflected' in self.__class__.__name__:
            return
        actual = self.provider.getDefaultValues('test_table')
        assert sorted(actual.keys()) == ['Integer', 'created'], sorted(actual.keys())
        assert actual['Integer'] == 10

class TestSAProvider(_TestSAProvider):
    pass


