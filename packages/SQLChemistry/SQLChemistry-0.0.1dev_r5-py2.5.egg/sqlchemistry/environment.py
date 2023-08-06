#environment.py

"""This contains the environment stuff for SQLChemistry

Copyright (C) 2008 Emanuel Gardaya Calso <egcalso@gmail.com>

This module is part of SQLChemistry and is is released under
the LGPL License
"""

import alchemy as orm

class Environment(object):
    """Environment object to be used as front-end of applications."""

    def __init__(self, conf):
        self.uri = conf.get_uri()
        conf.get_tables()
        self.engine = orm.engine.get_engine(self.uri)
        self.session = orm.orm.get_session(self.engine)
        self.schema = orm.schema.Schema(conf)
        self.schema.bind_engine(self.engine)
        self.tables = self.schema.get_tables()
        self.schema.create_classes()
        self.classes = self.schema.get_classes()
        self.schema.map_tables()


