"""
SessionConfig Module

The SessionConfig defines all of the Data related issues for dbsprockets

Classes:
Name                               Description
SessionConfig                      Parent Class
DatabaseSessionConfig
TableViewSessionConfig
AddRecordViewConfig
EditRecordSessionConfig

Exceptions:
None

Functions:
None

Copywrite (c) 2007 Christopher Perkins
Original Version by Christopher Perkins 2007
Released under MIT license.
"""
from cStringIO import StringIO
import types
from iprovider import IProvider
from dbsprockets.metadata import Metadata, DatabaseMetadata, FieldsMetadata, FieldMetadata
from dbsprockets.util import MultiDict, Label

class SessionConfig(object):
    metadata_type = Metadata
    def __init__(self, id, provider, identifier=None):
        if not isinstance(id, types.StringTypes):
            raise TypeError('id is not a string')
        if not isinstance(provider, IProvider):
            raise TypeError('provider is not of type IProvider')
        if identifier is not None and not isinstance(identifier, types.StringTypes):
            raise TypeError('identifier is not a string')
        self.id = id
        self.provider = provider
        self.identifier = identifier
        self.metadata = self.metadata_type(provider, identifier)

    def get_value(self, values={}):
        """get the value associated with the session
        Arguments:
        values : as provided from the browser
        """
        values = self._do_get_value(values=values)
        return values

    def get_count(self, values={}):
        return self._do_get_count(values)

    def _do_get_count(self, values={}):
        raise NotImplementedError

    def _do_get_value(self, values={}):
        #the default get_value is just a pass through
        return values

class DatabaseSessionConfig(SessionConfig):
    metadata_type = DatabaseMetadata

    def _do_get_value(self, values={}):
        r = {}
        tables = self.metadata.keys()
        for table in tables:
            r[table] = self.metadata[table]
        return r

class TableViewSessionConfig(SessionConfig):
    metadata_type = FieldsMetadata
    foreign_key_field_labels = ['name', '_name', 'description', '_description', 'title']

    def _do_get_foreign_key_dict(self):
        return self.provider.get_foreign_key_dict(self.identifier, self.foreign_key_field_labels)

    #for this class it makes a lot of sense to override the parent method
    def get_value(self, values={}, page=1, recordsPerPage=20):
        many_to_many_tables = self.provider.get_association_tables(self.identifier)
        table_name = self.identifier
        offset = (page - 1)*recordsPerPage
        rows = self.provider.select(table_name, result_offset=offset, result_limit=recordsPerPage)
        #this is probably going to have to be changed (too slow)
        foreign_key_dict = self._do_get_foreign_key_dict()
        primary_keys=self.provider.get_primary_keys(self.identifier)
        newRows = rows
        if len(rows) > 0:
            newRows = []
            for row in rows:
                d = {}
                for key in row.keys():
                    value = row[key]
                    d[key] = value
                    if key == 'password':
                        d[key] = '*'*6
                    if value is not None and key in foreign_key_dict and value in foreign_key_dict[key]:# and not key in primary_keys:
                        d[key] = Label(foreign_key_dict[key][value])
                        d[key].original=value
                    if self.provider.is_binary_column(self.identifier, key):
                        d[key] = '<file>'
                        if row[key] is None:
                            d[key] = ''

                if self.identifier not in many_to_many_tables:
                    many_to_many_columns = self.provider.get_many_to_many_columns(self.identifier)
                    for column in many_to_many_columns:
                        table_name = column[:-1] #strip off the 's'
                        many_to_many_table = self.provider.get_many_to_many_table(self.identifier, table_name)
                        sourcePK = self.provider.get_primary_keys(self.identifier)[0]
                        values = {sourcePK:row[sourcePK]}
                        view_column = self.provider.get_view_column_name(table_name)
                        id_column   = self.provider.get_primary_keys(table_name)[0]
                        selected_rows = self.provider.select(many_to_many_table, values=values, columns_limit=[id_column,])
                        values = MultiDict()
                        for item in selected_rows:
                            values[id_column] = item[id_column]
                        many_to_many_rows = []
                        if len(selected_rows) != 0:
                            many_to_many_rows = self.provider.select(table_name, values=values, whereclause_join='or', columns_limit=[view_column,])
                        many_to_many_labels = ''
                        for value in many_to_many_rows:
                            many_to_many_labels += unicode(value[view_column]) +', '
                        many_to_many_labels = many_to_many_labels[:-2]
                        d[column] = many_to_many_labels
                newRows.append(d)

        return newRows

    def _do_get_count(self, values={}):
        return self.provider.count(self.identifier)


class AddRecordSessionConfig(SessionConfig):
    metadata_type = FieldsMetadata

    def _do_get_value(self, values={}):
        #attach the tablename to the  values
        values['table_name'] = self.metadata.identifier
        values['dbsprockets_id'] =  self.id
        return values

class EditRecordSessionConfig(AddRecordSessionConfig):
    metadata_type = FieldsMetadata

    def _do_get_many_to_many(self, values={}):
        #most of this should probably go in provider
        table_name = self.identifier
        pk = self.provider.get_primary_keys(table_name)[0]
        src_table = self.provider.get_table(table_name)

        association_tables = self.provider.get_association_tables(table_name)
        for table in association_tables:
            table = self.provider.get_table(table)
            src_column, dst_column = table.c
            if src_column.foreign_keys[0].column.table != src_table:
                temp = src_column
                src_column = dst_column
                dst_column = temp
                table = src_column.table
            d = {src_column.name:values[str(pk)]}
            rows = self.provider.select(table.name, values=d)
            new_values = [row[dst_column] for row in rows]
            values[str('many_many_'+dst_column.foreign_keys[0].column.table.name)] = new_values
        return values

    def _do_get_value(self, values={}):
        if self.identifier not in self.provider.get_many_to_many_tables():
            values.update(self._do_get_many_to_many(values))
        values = super(EditRecordSessionConfig, self)._do_get_value(values)
        #sql object is not attachable, but a dictionary is

        row = self.provider.select_on_primary_keys(table_name=self.identifier, values=values)[0]
        values.update(row)
        return values
