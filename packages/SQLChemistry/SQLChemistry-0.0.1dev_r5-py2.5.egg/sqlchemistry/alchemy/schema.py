#schema.py

"""Module building ORM objects for database metadata

Copyright (C) 2008 Emanuel Gardaya Calso <egcalso@gmail.com>

This module is part of SQLChemistry and is is released under
the LGPL License
"""

from sqlalchemy.orm import mapper
from sqlalchemy.schema import MetaData
from sqlalchemy.schema import Table, Column, ForeignKey
from sqlalchemy.types import Integer


__all__ = [
        'Schema',
        'map_table',
    ]


class BaseTableClass(object):
    _tbl_name = ''

    def __init__(self, **kw):
        for k,v in kw.iteritems():
            setattr(self, k, v)

    def __str__(self):
        return '<%s %s>' % (
                self._tbl_name,
                self.id,
            )

def map_table(table, cls):
    mapper(cls, table)

def create_class(base_class=BaseTableClass):
    class TableClass(base_class):
        pass
    return TableClass



class Schema(object):
    '''Get schema objects from a given conf object.'''

    foreign_key_string = 'foreign:'

    def __init__(self, conf):
        self.meta = MetaData()
        self.conf = conf
        self.cols = []
        self.tables = {}
        self.table_classes = {}
        self.kwargs = dict(autoload=True)

    def bind_engine(self, engine):
        self.meta.bind = engine

    def create_classes(self, base_class=BaseTableClass):
        for k in self.conf.tables.keys():
            self.table_classes[k] = create_class(base_class)

    def get_classes(self):
        return self.table_classes

    def get_meta(self):
        return self.meta

    def get_table(self, name):
        self.cols = []
        self.kwargs = dict(autoload=True)
        details = self.conf.tables[name]
        details = self.process_custom_cols(**details)
        details = self.process_custom_args(**details)
        dict(autoload=True)
        return Table(name, self.meta, *self.cols, **self.kwargs)

    def get_tables(self):
        for k,v in self.conf.tables.iteritems():
            self.tables[k] = self.get_table(k)
        return self.tables

    def map_tables(self):
        for k,v in self.tables.iteritems():
            self.table_classes[k]._tbl_name = k
            map_table(v, self.table_classes[k])

    def process_custom_args(self, **kw):
        return kw

    def process_custom_cols(self, **kw):
        for col,val in dict(kw).iteritems():
            if val.startswith(self.foreign_key_string):
                key = val.replace(self.foreign_key_string, '')
                self.cols.append(Column(col, Integer, ForeignKey(key)))
                del kw[col]
        return kw


