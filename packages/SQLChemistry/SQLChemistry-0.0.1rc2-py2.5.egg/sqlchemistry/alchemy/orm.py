#orm.py

"""Module for creating SQLAlchemy orm objects

Copyright (C) 2008 Emanuel Gardaya Calso <egcalso@gmail.com>

This module is part of SQLChemistry and is is released under
the LGPL License
"""

from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.orm import mapper, relation

def get_session(engine):
    return scoped_session(sessionmaker(autoflush=True, transactional=True, bind=engine))

