"""
matadata Module

this contains the class which definies the generic interface for metadata
that is used in form generation later in the pipeline

Classes:
Name                               Description
Metadata                           general metadata function
DatabaseMetadata                   describes the fields as entries in the dictionary
FieldsMetadata                     describes the columns as entries in the dictionary
FieldMetadata                      generic type this is not used right now.

Exceptions:
MetadataError

Functions:
None

Copywrite (c) 2007 Christopher Perkins
Original Version by Christopher Perkins 2007
Released under MIT license.
"""
from dbsprockets.iprovider import IProvider

class MetadataError(Exception):pass
class NotFoundError(Exception):pass

class Metadata(dict):
    """
    """
    def __init__(self, provider, identifier=None):
        if not isinstance(provider, IProvider):
            raise TypeError('provider must be of type IProvider not %s'%type(provider))
        self.provider = provider
        self.identifier=identifier

    def __setitem__(self, key, value):
        self._do_check_set_item(key, value)
        dict.__setitem__(self, key, value)

    def __getitem__(self, item):
        try:
            value = self._do_get_item(item)
            return value
        except NotFoundError:
            return dict.__getitem__(self, item)

    def keys(self):
        r = self._do_keys()
        r.extend(dict.keys(self))
        return r
    def primary_keys(self):
        return self._do_get_primary_keys()

    @property
    def foreign_keys(self):
        return self._do_get_foreign_keys()

    @property
    def auto_increment_fields(self):
        return self._do_get_auto_increment_fields()

    def get_server_default(self, key):
        return self._do_get_server_default(key)
    def _do_get_auto_increment_fields(self):
        raise NotImplementedError
    def _do_get_foreign_keys(self):
        raise NotImplementedError
    def _do_get_primary_keys(self):
        raise NotImplementedError
    def _do_check_set_item(self, key, value):
        raise NotImplementedError
    def _do_get_item(self, item):
        raise NotImplementedError
    def _do_keys(self):
        raise NotImplementedError
    def _do_get_server_default(self,key):
        raise NotImplementedError

class DatabaseMetadata(Metadata):
    """
    """
    def __init__(self, provider, identifier=None):
        Metadata.__init__(self, provider, identifier)
        self._tables = None

    def _do_check_set_item(self, key, value):
        if key in self.provider.tables:
            raise MetadataError('%s is already a table name in the database'%key)

    def _do_get_primary_keys(self):
        return []
    
    
    def _do_get_foreign_keys(self):
        return []

    def _do_get_item(self, item):
        if item in self.provider.tables:
            return self.provider.get_table(item)
        raise NotFoundError

    def _do_keys(self):
        if self._tables is None:
            self._tables = self.provider.get_tables()
        return self._tables

class FieldsMetadata(Metadata):
    """
    """
    def __init__(self, provider, identifier):
        Metadata.__init__(self, provider, identifier)
        self.table = self.provider.get_table(identifier)

    def _do_check_set_item(self, key, value):
        if key in self.table.columns:
            raise MetadataError('%s is already found in table: %s'%(key, self.table))

    def _do_get_item(self, item):
        if item in self.table.columns:
            return self.table.columns[item]
        raise NotFoundError

    def _do_get_auto_increment_fields(self):
        return self.provider.get_auto_increment_fields(self.identifier)

    def _do_get_primary_keys(self):
        return self.provider.get_primary_keys(self.identifier)

    def _do_get_foreign_keys(self):
        return [c.name for c in self.provider.get_foreign_keys(self.identifier)]

    def _do_keys(self):
        r = self.table.columns.keys()
        return r
    
    def _do_get_server_default(self,key):
        return self.provider.get_server_default(self.identifier,key)
class FieldMetadata(Metadata):
    """
    """
    pass

