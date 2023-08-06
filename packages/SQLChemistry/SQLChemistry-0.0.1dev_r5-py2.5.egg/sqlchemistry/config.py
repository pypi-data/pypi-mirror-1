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
            if isinstance(v, dict):
                self.tables[k] = v
        return self.tables


