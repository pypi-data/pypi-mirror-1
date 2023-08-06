"""
saprovider Module

this contains the class which allows dbsprockets to interface with sqlalchemy.

Classes:
Name                               Description
SAProvider                         sqlalchemy metadata/crud provider

Exceptions:
None

Functions:
None


Copywrite (c) 2007 Christopher Perkins
Original Version by Christopher Perkins 2007
Released under MIT license.
"""

from sqlalchemy import *
from dbsprockets.iprovider import IProvider
from cgi import FieldStorage
from datetime import datetime

class SAProvider(IProvider):
    """A Class to manipulate an sqlalchemy interface.

    Functions:
    get_tables      get a list of tables from the database
    get_table       get the table definition for a given table
    get_columns     get the columns from a given table
    get_primary_keys get the primary keys from a given table.

    Attributes:
    metadata       link to the sqlalchemy metadata
    """
    where_clause_join_funcs = {'and':and_, 'or':or_}

    def __init__(self, metadata):
        if not isinstance(metadata, MetaData):
            raise TypeError('metadata is not of type sqlalchemy.MetaData')
        self.metadata = metadata
        self.tables = {}
        for name, table in metadata.tables.iteritems():
            self.tables[name] = table

    def get_tables(self):
        """()->[list of tablesNames]
        get a list of tables from the database"""
        return self.metadata.tables.keys()
    tables = property(get_tables)

    def get_table(self, name):
        """(name) -> sqlalchemy.schema.Table
        get the table definition with the given table name
        """
        if hasattr(self.metadata, 'schema'):
            schema = self.metadata.schema
            if schema and not name.startswith(schema):
                name = '.'.join((schema, name))
        return self.metadata.tables[name]

    def get_columns(self, table_name):
        """(name) -> [list of column_names]
        get the column names given the table name
        """
        return self.get_table(table_name).columns.keys()

    def get_column(self, table_name, name):
        """(table_name, name) -> sqlalchemy.schema.Column
        get the column definition givcen the tablename and column name.
        """
        return self.get_table(table_name).columns[name]

    def get_primary_keys(self, table_name):
        """(name) -> [list of column_names that are primary keys]
        get a list of columns which are primary keys
        """
        table = self.get_table(table_name)
        return table.primary_key.keys()

    def get_auto_increment_fields(self, table_name):
        table = self.get_table(table_name)
        return [c.name for c in table.c if c.autoincrement]

    def getDefaultValues(self, table_name):
        table = self.get_table(table_name)
        r = {}
        for c in table.c:
            if c.default is not None:
                r[c.name] = c.default.execute()
        return r

    def _generate_whereclause(self, table, pks, values={}, join='and'):
        l = [(getattr(table.c, key)==value) for key, value in values.iteritems() if key in pks and hasattr(table.c, key)]
        whereclause = None
        #one primary key
        if len(l) == 1:
            whereclause = l[0]
        #case of multiple keys
        elif len(l) > 1:
            join_func = self.where_clause_join_funcs[join]
            whereclause = join_func(*l)
        return whereclause

    def _generateColumnListing(self, table, column_names):
        l = [getattr(table.c, key) for key in column_names if hasattr(table.c, key)]
        return l

    def _removePrimaryKeys(self, table_name, values={}):
        for key in self.get_primary_keys(table_name):
            if key in values:
                values.pop(key)
        return values

    def _remove_primary_keys_if_not_foreign(self, table_name, values={}):
        foreign_keys=[c.name for c in self.get_foreign_keys(table_name)]
        for key in self.get_primary_keys(table_name):
            if (key in values) and (not (key in foreign_keys)):
                values.pop(key)
        return values


    def _remove_non_limit_columns(self, values, limit):
        if limit is None:
            return values
        for key in values.keys():
            if key not in limit:
                values.pop(key)
        return values

    def get_foreign_keys(self, table_name):
        table = self.get_table(table_name)
        return [column for column in table.columns if len(column.foreign_keys)>0]

    def get_foreign_key_dict(self, table_name, foreign_key_field_labels=['name', '_name', 'description', '_description', 'title']):
        """Returns a dict of dicts where the keys are the column names, and then the row values.  Something like this:
        {town_table:{1:'Arvada', 2:'Denver', 3:'Golden'}}
        """
        d = {}
        foreignKeyColumns = self.get_foreign_keys(table_name)
        for column in foreignKeyColumns:
            table = column.foreign_keys[0].column.table
            foreign_table_name = table.name
            rows      = table.select().execute().fetchall()
            if len(rows) == 0:
                d[column.name] = {}
                continue
            view_column = self._find_first_column(foreign_table_name, foreign_key_field_labels)
            id_column   = self._find_first_column(foreign_table_name, ['_id', 'id'])
            innerD = {}
            for row in rows:
                innerD[row[id_column]] = row[view_column]
            d[column.name] = innerD
        return d

    def get_many_to_many_tables(self):
        if not hasattr(self, '_many_to_many_tables'):
            self._many_to_many_tables = [table for table in self.tables if len(self.get_foreign_keys(table)) == 2 and len(self.get_columns(table)) == 2]
        return self._many_to_many_tables

    def get_many_to_many_columns(self, table_name):
        table = self.get_table(table_name)
        many_to_many_tables = self.get_association_tables(table_name)
        many_to_many_columns = []
        for many_to_many_table in many_to_many_tables:
            column1, column2 = self.get_table(many_to_many_table).columns
            if column1.foreign_keys[0].column.table == table:
                many_to_many_columns.append(column2.foreign_keys[0].column.table.name+'s')
            else:
                many_to_many_columns.append(column1.foreign_keys[0].column.table.name+'s')
        return many_to_many_columns

    def get_many_to_many_table(self, table_name1, table_name2):
        table1 = self.get_table(table_name1)
        table2 = self.get_table(table_name2)
        for table in self.get_many_to_many_tables():
            tables = [column.foreign_keys[0].column.table for column in self.get_table(table).columns]
            if table1 in tables and table2 in tables:
                return table

    def get_association_tables(self, table_name):
        tables = []
        src_table = self.get_table(table_name)
        for table in self.get_many_to_many_tables():
            for column in self.get_table(table).columns:
                key = column.foreign_keys[0]
                if key.column.table is src_table:
                    tables.append(table)
                    break
        return tables

    def set_many_to_many(self, src_table_name, srcID, related_table_name, values):
        src_table = self.get_table(src_table_name)
        related_table = self.get_table(related_table_name)

        many_to_many_tables = self.get_many_to_many_tables()
        found_table = None
        #find the right table to modify
        for table in many_to_many_tables:
            table = self.get_table(table)
            column1, column2 = table.c
            if column1.foreign_keys[0].column.table == src_table and column2.foreign_keys[0].column.table == related_table:
                found_table = table
                break;
            if column2.foreign_keys[0].column.table == src_table and column1.foreign_keys[0].column.table == related_table:
                found_table = table
                (column1,column2)=(column2,column1)
                break;
        if found_table is None:
            return
        #clear it out
        found_table.delete(whereclause=column1==srcID).execute()

        #add the new values
        for value in values:
            found_table.insert(values={column1:srcID, column2:value}).execute()

        #this operation was successful
        return True

    def get_associated_many_to_many_tables(self, table_name):
        tables =self.get_association_tables(table_name)
        src_table = self.get_table(table_name)
        r = []
        for table in tables:
            for column in self.get_table(table).columns:
                key = column.foreign_keys[0]
                if key.column.table is not src_table:
                    r.append(key.column.table.name)
                    continue
        return r

    def _find_first_column(self, table_name, possible_columns):
        actual_columns = self.get_columns(table_name)
        view_column = None
        for column_name in possible_columns:
            for actual_name in actual_columns:
                if column_name in actual_name:
                    view_column = actual_name
                    break
            if view_column:
                break;
        if view_column is None:
            view_column = actual_columns[0]
        return view_column

    def is_binary_column(self, table_name, column_name):
        return column_name in self.get_columns(table_name) and isinstance(self.get_column(table_name, column_name).type, Binary)

    def get_view_column_name(self, table_name, possible_columns=['_name', 'name', 'description', 'title']):
        return self._find_first_column(table_name, possible_columns)

    def get_id_column_name(self, table_name):
        possible_columns = ['_id', 'id']
        return self._find_first_column(table_name, possible_columns)

    def _select(self, table_name, pks, values, columns_limit, result_limit, result_offset, whereclause_join='and'):
        order_by = pks
        table = self.get_table(table_name)
        whereclause = self._generate_whereclause(table, pks, values, whereclause_join)
        column_listing=[table]
        if columns_limit is not None:
            column_listing = self._generateColumnListing(table, columns_limit)
            order_by      = column_listing
        s = select(column_listing, whereclause).offset(result_offset).limit(result_limit).order_by(*list(table.c))
        return s.execute().fetchall()

    def is_unique(self, field, value):
        s = select([field,], whereclause=field==value).execute().fetchall()
        return len(s) == 0
    def get_server_default(self,table_name,key):
        table=self.get_table(table_name)
        column=table.c.get(key)
        return column.server_default
    #crud below
    def select_on_primary_keys(self, table_name, values={}, columns_limit=None, result_limit=None, result_offset=None):
        pks = self.get_primary_keys(table_name)
        return self._select(table_name, pks, values, columns_limit, result_limit, result_offset)

    def select(self, table_name, values={}, columns_limit=None, result_limit=None, result_offset=None, whereclause_join='and'):
        pks = values.keys()
        return self._select(table_name, pks, values, columns_limit, result_limit, result_offset, whereclause_join)

    def count(self, table_name, values=None):
        table = self.get_table(table_name)
        return table.select().alias('all_data').count().execute().fetchall()[0][0]

    def add(self, table_name=None, values={}, columns_limit=None):
        for key, value in values.iteritems():
            if isinstance(value, FieldStorage):
                values[key] = value.value

        #remove the primary keys which could cause a conflict
        kw = self._remove_primary_keys_if_not_foreign(table_name, values)
        #kw=self._removePrimaryKeys(table_name, values)
        from sys import stderr
        values = self._remove_non_limit_columns(values, columns_limit)
        table = self.get_table(table_name)
        values = self._modify_values_for_dates(table, values)
        table.insert(values=kw).execute()

    def delete(self, table_name, values={}):
        table = self.get_table(table_name)
        pks = self.get_primary_keys(table_name)
        whereclause = self._generate_whereclause(table, pks, values)
        return table.delete(whereclause).execute()

    def _modify_values_for_dates(self, table, values):
        for key, value in values.iteritems():
            if key in table.columns and value is not None:
                if isinstance(table.columns[key].type, DateTime) and not isinstance(value, datetime):
                    dt = datetime.strptime(value[:19], '%Y-%m-%d %H:%M:%S')
                    values[key] = dt
                if isinstance(table.columns[key].type, Date) and not isinstance(value, datetime):
                    dt = datetime.strptime(value, '%Y-%m-%d')
                    values[key] = dt
        return values


    def edit(self, table_name, values={}, columns_limit=None):
        pks = self.get_primary_keys(table_name)
        table = self.get_table(table_name)
        values = self._remove_non_limit_columns(values, columns_limit)
        values = self._modify_values_for_dates(table, values)
        whereclause = self._generate_whereclause(table, pks, values)
        #remove the primary keys which could cause a conflict
        kw = self._removePrimaryKeys(table_name, values)
        table = self.get_table(table_name)

        values = self._modify_values_for_dates(table, values)

        if len(kw)>0:
            table.update(values=kw, whereclause=whereclause).execute()
    def is_nullable_field(self,field):
        return field.nullable

    def create_relationships(self, table_name, params):
        #this might become a decorator
        #check to see if the table is a many-to-many table first
        if table_name in self.get_many_to_many_tables():
            return
        #right now many-to-many only supports single primary keys
        pk=self.get_primary_keys(table_name)
        assert len(pk)==1
        id = params.get(pk[0], None)
        relationships = {}



        #clear out any existing relationships (in the case that a parameter is blank, and therefore not in the params list)
        if id != '' and id is not None:
            for table in self.get_associated_many_to_many_tables(table_name):
                if 'many_many_'+table not in params:
                    self.set_many_to_many(table_name, id, table, [])

        for key, value in params.iteritems():
            if key.startswith('many_many_'):
                relationships.setdefault(key[10:], []).append(value)
        for key, value in relationships.iteritems():
            self.set_many_to_many(table_name, id, key, value)

