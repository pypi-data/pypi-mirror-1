#__init__.py

"""Package for SQLChemistry

Sample Usage:

* To load a config file:
    conf = Config('filename.ini')
* To create an environment:
    env = Environment(conf)
* A dictionary whose keys are table names and values are the table objects:
    env.tables
* A dictionary whose keys are table names and values are the classes mapped to the table objects:
    env.classes

Copyright (C) 2008 Emanuel Gardaya Calso <egcalso@gmail.com>

This module is part of SQLChemistry and is is released under
the LGPL License
"""

__author__ = 'Emanuel Gardaya Calso <egcalso@gmail.com>'
__version__ = '0.0.1'

from config import Config
from environment import Environment
from alchemy.orm import get_session
from alchemy.engine import get_engine
from alchemy.schema import Schema, map_table, create_class, BaseTableClass

