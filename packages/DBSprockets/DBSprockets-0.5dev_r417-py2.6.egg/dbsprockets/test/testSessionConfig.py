from nose.tools import raises, eq_
from dbsprockets.sessionconfig import *
from dbsprockets.saprovider import SAProvider
from dbsprockets.test.base import *
from dbsprockets.test.model import *
from dbsprockets.iprovider import IProvider
from cStringIO import StringIO
from cgi import FieldStorage

def setup():
    setupDatabase()

class TestSessionConfig(DBSprocketsTest):
    obj = SessionConfig
    provider = IProvider()
    identifier = None

    def setup(self):
        self.config = self.obj('', self.provider, self.identifier)
        super(TestSessionConfig, self).setup()

    def test_create(self):
        pass

    @raises(TypeError)
    def _create(self, arg1, arg2=IProvider(), arg3=''):
        self.obj(arg1, arg2, arg3)

    def test_createObjBad(self):
        badInput = ('a', (), {}, [], 1, 1.2)
        for input in badInput[1:]:
            yield self._create, input
        for input in badInput:
            yield self._create, '', input
        for input in badInput[1:]:
            yield self._create, '', self.provider, input

    def test_value(self):
        eq_(self.config.get_value(values={}), {})

    @raises(NotImplementedError)
    def testCount(self):
        self.config.get_count()

class TestDatabaseSessionConfig(TestSessionConfig):
    obj = DatabaseSessionConfig
    provider = SAProvider(metadata)

    def test_value(self):
        value = sorted(self.config.get_value())
        expected = sortedTableList
        assert value == expected, "expected: %s\nactual: %s"%(expected, value)

class TestAddRecordSessionConfig(TestSessionConfig):
    obj = AddRecordSessionConfig
    provider = SAProvider(metadata)
    identifier = 'test_table'

    def test_value(self):
        value = self.config.get_value(values={})
        expected = {'dbsprockets_id': '', 'table_name': 'test_table'}
        assert value == expected, "expected: %s\nactual: %s"%(expected, value)

class TestEditRecordSessionConfig(TestSessionConfig):
    obj = EditRecordSessionConfig
    provider = SAProvider(metadata)
    identifier = 'tg_user'

    def test_value(self):
        actual = self.config.get_value(values=dict(user_id=self.user.user_id))
        expected = {'table_name': 'tg_user',
                    u'password': u'asdf',
                    u'user_name': u'asdf'}
        for key, value in expected.iteritems():
            assert actual[key] == value, "expected: %s\nactual: %s\nkey: %s"%(expected, actual, key)

    def test_do_get_many_to_many(self):
        config = self.obj('', self.provider, 'tg_group')
        actual = config._do_get_many_to_many(values=dict(group_id=self.user.groups[0].group_id))
        expected =  {'many_many_permission': [], }
        for key, value in expected.iteritems():
            eq_((key, value), (key, actual[key]))


class TestTableViewSessionConfig(TestSessionConfig):
    obj = TableViewSessionConfig
    provider = SAProvider(metadata)
    identifier = 'tg_user'

    def test_value(self):
        actual = self.config.get_value()
        assert len(actual) == 1
        expected = {'user_name': u'asdf', 'password':u'******'}
        actual = actual[0]
        for key, value in expected.iteritems():
            assert actual[key] == value, "expected: %s\nactual: %s"%(expected, actual)

    def testValueWithFile(self):
        config = TableViewSessionConfig('id', self.provider, 'test_table',)
        actual = config.get_value()

    def testCount(self):
        eq_(1, self.config.get_count())


class TestTableViewSessionConfigLabel(TestSessionConfig):
    obj = TableViewSessionConfig
    provider = SAProvider(metadata)
    identifier = 'user_reference'

    def test_value(self):
        actual = self.config.get_value()[0]
        eq_(actual, {'user_id':'asdf'})

    def testCount(self):
        eq_(1, self.config.get_count())

