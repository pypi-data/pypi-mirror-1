#config.py

"""This contains the configuration variables for SQLChemistry

Copyright (C) 2008 Emanuel Gardaya Calso <egcalso@gmail.com>

This module is part of SQLChemistry and is is released under
the LGPL License
"""

from configobj import ConfigObj


class Config(object):
    """Custom configuration object for SQLChemistry.
    
    This exposes:
     * conf - the original configuration object
     * uri - the database uri in the configuration object
     * tables - the part of the configobj that pertains to tables
    """

    def __init__(self, file):
       self.file = file
       self.conf = ConfigObj(file)

    def get_uri(self):
        self.uri = self.conf['uri']
        return self.uri

    def get_tables(self):
        """Expose tables from the self.conf configuration object"""
        self.tables = {}
        for k,v in self.conf.iteritems():
            if k.startswith('table:'):
                tbl_name = k.lstrip('table:')
                self.tables[tbl_name] = v
        return self.tables

    def get_columns(self, tbl_name):
        columns = {}
        for k, v in self.tables.iteritems():
            if k.startswith('column:'):
                col_name = k.lstrip('column:')
                columns[col_name] = v
        return columns


