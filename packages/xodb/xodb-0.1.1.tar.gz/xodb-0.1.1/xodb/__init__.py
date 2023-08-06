from __future__ import absolute_import

import tempfile
import xapian

from . import exc
from . database import Database, Record, MultipleValueRangeProcessor, instance_factory
from . schema import Schema, Attribute
from . types import String, Numeric, Text, Sequence, Mapping, Date, Datetime


def open(path_or_db, writable=True, overwrite=False, spelling=True, record_factory=Record):
    """Return an xodb database with the given path or xapian database object.

    :param path_or_db: A path to a database file or a pre-existing xapian database object.

    :param writable: Open database in writable mode.

    :param overwrite: If writable is True, overwrite the existing
    database with a new one.

    :param spelling: If True, write spelling correction data to the
    database.

    :param record_factory: Callable factory to pass stored object
    state when results are instanciated.
    """
    return Database(path_or_db, writable=writable, overwrite=overwrite, 
                    spelling=spelling, record_factory=record_factory)


def temp(record_factory=Record, spelling=True):
    """Returns an xodb database backed by a teporary directory.  You
    are responsible for cleaning up the directory.

    :param spelling: If True, write spelling correction data to database.

    :param record_factory: Callable factory to pass stored object
    state when results are instanciated.
    """ 
    return open(tempfile.mkdtemp(), spelling=spelling, record_factory=record_factory)


def inmemory(record_factory=Record):
    """Returns an xodb database backed by an in-memory xapian
    database.  Does not support spelling correction.

    :param record_factory: Callable factory to pass stored object
    state when results are instanciated.
    """
    return open(xapian.inmemory_open(), spelling=False, record_factory=record_factory)
