#exceptions.py

"""Exceptions used with SQLChemistry

The base exception class is SQLChemistryError.

Copyright (C) 2008 Emanuel Gardaya Calso <egcalso@gmail.com>

This module is part of SQLChemistry and is is released under
the LGPL License
"""

class SQLChemistryError(Exception):
    """Generic error class."""


# Warnings
class SCDeprecationWarning(DeprecationWarning):
    """Issued once per usage of a deprecated API."""

class SCPendingDeprecationWarning(PendingDeprecationWarning):
    """Issued once per usage of a future deprecated API."""

class SCWarning(RuntimeWarning):
    """Issued at runtime."""


