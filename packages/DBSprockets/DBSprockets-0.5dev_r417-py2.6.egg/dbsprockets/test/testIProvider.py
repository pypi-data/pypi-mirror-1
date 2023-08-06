from nose.tools import raises
from dbsprockets.iprovider import IProvider
from dbsprockets.test.base import DBSprocketsTest, setupDatabase, teardownDatabase

session = None
engine = None
connect = None

def setup():
    global session, engine, connect
    session, engine, connect = setupDatabase()
def teardown():
    pass

class TestIProvider(object):
    def setup(self):
        self.provider = IProvider()
#        super(TestIProvider, self).setup()

    def test_create(self):
        pass

    @raises(NotImplementedError)
    def test_get_tables(self):
        tables = sorted(self.provider.get_tables())

    @raises(NotImplementedError)
    def testGetTable(self):
        table = self.provider.get_table('tg_user')

    @raises(NotImplementedError)
    def testGetColumns(self):
        columns = self.provider.get_columns('tg_user')

    @raises(NotImplementedError)
    def testGetColumn(self):
        column = self.provider.get_column('tg_user', 'user_id')

    @raises(NotImplementedError)
    def testGetPrimaryKeys(self):
        keys = self.provider.get_primary_keys('tg_user')

    @raises(NotImplementedError)
    def testSelect(self):
        rows = self.provider.select('tg_user')

    @raises(NotImplementedError)
    def test_add(self):
        self.provider.add()

    @raises(NotImplementedError)
    def test_edit(self):
        self.provider.edit()