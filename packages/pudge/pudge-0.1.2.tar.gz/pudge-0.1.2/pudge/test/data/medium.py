#!/usr/bin/env python
"""Documentation comment..

Here's some more text..

"""

# Here's a multiline comment.
# Did I mention is spans multiple lines?

__revision__ = "$Revision: 5 $"
__date__ = "$Date: 2005-05-25 20:04:35 -0700 (Wed, 25 May 2005) $"
__author__ = "Ryan Tomayko (rtomayko@gmail.com)"
__copyright__ = "Copyright 2005, Ryan Tomayko"
__license__ = "MIT <http://www.opensource.org/licenses/mit-license.php>"

import os
import sys
import new

import activerecord.naming as naming
from activerecord.connection import Connection
from activerecord import SQL

class ModelType(type):
    
    table_name = None
    primary_key = 'id'
    column_map = None
    
    # lazy attributes
    _connection = None
    _columns = None
    _column_dict = None
    _column_names = None
    
    def __init__(c, classname, bases, attrs):
        super(ModelType, c).__init__(classname, bases, attrs)
        if classname in ('Model', ):
            return
        classname = naming.CamelName(classname)
        classname.chomp('Model') # remove model suffix if it exists
        attr_keys = attrs.keys()
        if not 'table_name' in attr_keys:
            c.table_name = str(classname.to_under())                
        
    def load_attributes(self):
        # XXX thread safety? need to understand what the GIL does for me..
        if hasattr(self, '_attributes_loaded'):
            return
        self._attributes_loaded = 1
        def template_get(name):
            fct = lambda self : self.read_attribute(name)
            return fct
        def template_set(name):
            fct = lambda self, v: self.write_attribute(name, v)
            return fct
        for name in self.attribute_names:
            if hasattr(self, name):
                continue
            else:
                get_func = getattr(self, 'get_%s' % name, None) or template_get(name)
                set_func = getattr(self, 'set_%s' % name, None) or template_set(name)
                prop = property(get_func, set_func)
                setattr(self, name, prop)        
        
    def set_connection(self, url):
        self._connection = Connection(url)
    
    def get_connection(self):
        return self._connection or Connection()
    
    connection = property(get_connection, set_connection)
    
    def reset_columns(self):
        self._columns = None
        self._column_dict = None
        self._column_names = None

    @property
    def columns(self):
        if self._columns is None:
            cnn = self.connection
            if cnn is not None:
                self._columns = cnn.get_columns(self.table_name)
        return self._columns

    @property
    def column_dict(self):
        if self._column_dict is None:
            self._column_dict = d = {}
            for c in self.columns:
                d[c.name] = c
        return self._column_dict
    
    @property
    def column_names(self):
        if self._column_names is None:
            names = self.columns
            if names is not None:
                self._column_names = [c.name for c in names]
        return self._column_names

    # TODO seperate column and attribute names..
    attribute_names = column_names
    
    def column_names_for_query(self, pk=1):
        names = self.column_names
        if not pk:
            primary_key = self.primary_key
            names = [c for c in names if c != primary_key]
        return ', '.join(names)
    
    def count(self, conditions=None):
        sql = SQL("SELECT COUNT(%s) FROM %s"
                  % (self.primary_key, self.table_name))
        if conditions:
            sql << 'WHERE' << SQL(conditions, 2)
        return self.connection.select_scalar(sql)
    
    def exists(self, id):
        return self.count("id = $id") > 0
    
    def load(self, columns, row_data):
        """
        Load a Model instance and call __dbinit__.
        
        :Parameters:
        
           - `row_data`: is a sequence of values retrieved from the database.
           - `columns`: is a the sequence of column names corresponding to
             each item in ``row_data``.
           
        The `row_data` and `columns` sequences must be of the same
        length.
        """
        lookup = self.column_dict.get
        row = zip([lookup(c) for c in columns], row_data)
        inst = object.__new__(self)
        inst.__dbinit__(row)
        return inst
    
    def find(self, id):
        columns = self.column_names
        sql = SQL("SELECT %s FROM %s WHERE %s = $id" %
                  (','.join(columns), self.table_name, self.primary_key))
        row = self.connection.select_one(sql)
        if row:
            return self.load(columns, row)
    
    def find_all(self, conditions=None, order=None, limit=None, offset=None):
        columns = self.column_names
        sql = SQL("SELECT %s FROM %s" %
                  (','.join(columns), self.table_name))
        if conditions:
            sql << "WHERE" << SQL(conditions, 2)
        if order:
            sql << SQL(order, 2)
        def generator():
            for row in self.connection.select(sql):
                yield self.load(columns, row)
        return generator()
    
    def find_by_sql(self, sql):
        sql = SQL(sql, 2)
        rs = self.connection.select(sql)
        columns = self.connection.column_names_from_cursor()
        def generator():
            for row in rs:
                yield self.load(columns, row)
        return generator()
    
    def delete(self, id):
        sql = SQL("DELETE %s WHERE %s = $id"
                  % (self.table_name, self.primary_key))
        return self.connection.delete(sql)
    
    def delete_all(self, conditions=None):
        sql = SQL("DELETE %s WHERE " % self.table_name) + SQL(conditions, 2)
        return self.connection.delete(sql)


class Model(object):
    __metaclass__ = ModelType
    attributes = None
    
    def __init__(self, **kw):
        # loads class level attributes if first time
        self.__class__.load_attributes()
        self.attributes = {}
        for k, v in kw.items():
            setattr(self, k, v)
        
    def __dbinit__(self, row):
        c = self.__class__
        c.load_attributes()
        self.attributes = {}
        load_attribute = self.load_attribute
        for col, val in row:
            # TODO column to attribute name conversion
            load_attribute(col.name, col, val)
    
    def load_attribute(self, name, column, value):
        """Load attribute value from database column value."""
        if value is None:
            value = column.default
        self.attributes[name] = value
    
    def save_attribute(self, name, column, value):
        """Prepare an attribute for storage."""
        return (name, column, value)
    
    def attribute_names(self):
        return self.__class__.attribute_names
    attribute_names = property(attribute_names)
    
    def column_for_attribute(self, name):
        return self.__class__.column_dict.get(name)
    
    def read_attribute(self, name):
        try:
            return self.attributes[name]
        except KeyError:
            if name in self.attribute_names:
                column = self.column_for_attribute(name)
                # TODO we need to make sure we have a chance to modify the...
                #      column default via write_attribute or this will be
                #      different from when the data is loaded normally
                self.write_attribute(name, column.default)
                return self.attributes[name]
            else:
                raise AttributeError(name)
        return
    
    def write_attribute(self, name, value):
        if name not in self.attribute_names:
            raise AttributeError(name)
        self.attributes[name] = value
        
    def save(self):
        if self.isnew:
            return self.insert()
        else:
            return self.update()
    
    def insert(self):
        assert self.isnew
        c = self.__class__
        column_names = c.column_names
        attr_values = [getattr(self, self.column_map.get(nm, nm))
                       for nm in column_names]
        table_name = c.table_name
        id = c.insert("INSERT %s (%s) VALUES ($attr_values)"
                      % (table_name, column_names))
        self.write_attribute(c.primary_key, id)
    
    def update(self):
        c = self.__class__
        names = self.dirty
        if not names:
            return
        values = [getattr(self, nm) for nm in column_names]
        sql = SQL("UPDATE %s SET" % self.table_name)
        for i, name, val in zip(range(len(names)), names, values):
            sql += SQL(" %s = ${val} " % name)
        c.update(sql)
    
