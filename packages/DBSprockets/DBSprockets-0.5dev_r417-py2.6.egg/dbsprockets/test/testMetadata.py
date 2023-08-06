from nose.tools import raises, eq_

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from dbsprockets.metadata import Metadata, MetadataError, DatabaseMetadata, FieldsMetadata, FieldMetadata
from dbsprockets.saprovider import SAProvider
from dbsprockets.test.base import sortedTableList
from dbsprockets.iprovider import IProvider
from dbsprockets.test.base import setupDatabase, DBSprocketsTest

import model
from model import *
session = None
engine = None
connect = None
trans = None

def setup():
    global session, engine, connect, trans
    session, engine, connect = setupDatabase()
#    trans = engine.begin()

provider = SAProvider(metadata)

class TestMetadata(DBSprocketsTest):
    obj = Metadata
    provider = IProvider()

    def setup(self):
        super(TestMetadata, self).setup()
        self.metadata = self.obj(self.provider)

    def test_create(self):
        pass

    @raises(TypeError)
    def _create(self, arg1):
        Metadata(arg1)

    def test_create_bad(self):
        badInput = ((), [], {}, 'a', 1, 1.2)
        for input in badInput:
            yield self._create, input

    @raises(NotImplementedError)
    def testPrimaryKeys(self):
        self.metadata.primary_keys()
    @raises(NotImplementedError)
    def testSetItem(self):
        self.metadata['asdf'] = 'asdf'
    @raises(NotImplementedError)
    def testGetItem(self):
        value = self.metadata['asdf']
    @raises(NotImplementedError)
    def testKeys(self):
        value = self.metadata.keys()
    @raises(NotImplementedError)
    def testAutoIncrementFields(self):
        value = self.metadata.auto_increment_fields

class TestDatabaseMetadata(TestMetadata):
    def setup(self):
        super(TestDatabaseMetadata, self).setup()
        self.metadata = DatabaseMetadata(provider)
    def testKeys(self):
        tables = sorted(self.metadata.keys())
        expected = sortedTableList
        assert tables == expected, "expected: %s\n actual: %s"%(expected, tales)
    def testSetItem(self):
        self.metadata['asdf'] = 'asdf'
    def testGetItem(self):
        table = self.metadata['test_table']
    def testGetAddedInfo(self):
        self.metadata['asdf'] = 'asdf'
        assert self.metadata['asdf'] == 'asdf'
    @raises(MetadataError)
    def testSetItemBad(self):
        self.metadata['test_table'] = '1234'
    def testPrimaryKeys(self):
        assert [] == self.metadata.primary_keys()
    def testGetForeignKeys(self):
        metadata = DatabaseMetadata(provider)
        pks = metadata.foreign_keys
        assert [] == pks, "%s"%pks

class TestFieldsMetadata(TestMetadata):
    def setup(self):
        super(TestFieldsMetadata, self).setup()
        self.metadata = FieldsMetadata(provider, 'test_table')

    def testGetItem(self):
        field = self.metadata['id']
        assert field.name == 'id'

    def testAutoIncrementFields(self):
        #this is expected input for SA, but I think we can do better
        value = self.metadata.auto_increment_fields
        eq_(value, ['id', 'created', 'BLOB', 'BOOLEAN_', 'Binary',
                    'Boolean', 'CHAR', 'CLOB', 'DATE_', 'DATETIME_',
                    'DECIMAL', 'Date', 'DateTime', 'FLOAT_',
                    'Float', 'INT', 'Integer', 'Numeric', 'PickleType',
                    'SMALLINT', 'SmallInteger', 'String', 'TEXT', 'TIME_',
                    'Time', 'TIMESTAMP', 'Unicode', 'VARCHAR', 'Password'])

    @raises(KeyError)
    def testGetItemKeyError(self):
        self.metadata['asdf']

    def testSetItem(self):
        self.metadata['asdf'] = '1234'
        assert self.metadata['asdf'] == '1234'

    @raises(MetadataError)
    def testSetItemBad(self):
        self.metadata['id'] = '1234'

    def testKeys(self):
        self.metadata['asdf'] = '1234'
        keys = sorted(self.metadata.keys())
        assert keys ==['BLOB', 'BOOLEAN_', 'Binary', 'Boolean', 'CHAR', 'CLOB', 'DATETIME_', 'DATE_', 'DECIMAL', 'Date', 'DateTime', 'FLOAT_', 'Float', 'INT', 'Integer', 'Numeric', 'Password', 'PickleType', 'SMALLINT', 'SmallInteger', 'String', 'TEXT', 'TIMESTAMP', 'TIME_', 'Time', 'Unicode', 'VARCHAR', 'asdf', 'created', 'id'], "actual: %s"%keys

    def testPrimaryKeys(self):
        pks = self.metadata.primary_keys()
        assert ['id',] == pks, "%s"%pks

    def testGetForeignKeys(self):
        metadata = FieldsMetadata(provider, 'tg_user')
        pks = metadata.foreign_keys
        assert ['town',] == pks, "%s"%pks
