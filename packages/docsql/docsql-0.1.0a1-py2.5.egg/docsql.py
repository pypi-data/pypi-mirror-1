#!/usr/bin/env python
from __future__ import division

__version__ = "$Revision: 1.11 $"

"""
docsql: easy access to Python DB API databases

>>> import docsql
>>> import MySQLdb
>>> connection = MySQLdb.connect("ensembldb.ensembl.org", "anonymous",
...                              db="ensembl_compara_28_1")
"""

from cPickle import dumps
from new import classobj
import sys

connection = None # global
# XXX: this should be a property that would keep you from overwriting
# it before it is closed

def _ordered_property(key):
    def get(self):
        return self[key]

    return property(get)

def subclass(cls, cls_dict, name="subclass()"):
    """
    dynamically create a new subclass of cls
    """
    name = "%s [%s]" % (cls.__name__, name)
    baseclasses = (cls,)

    return classobj(name, baseclasses, cls_dict)

class Row(tuple):
    """
    tuple (immutable)

    You can access columns by:
    * index: row[0]
    * attribute: row.id
    * key: row["id"]

    Having columns with names like "__getitem__" causes undefined
    behavior. Changing instance attributes causes undefined behavior.

    Note: the class is modified before instantiation by an Operation
    instance, so it will have different behavior than if you
    instantiated it directly.
    """

    # XXX: you can fix the method customization undefined behavior by
    # overriding __getattribute__()

    def __getitem__(self, key):
        try:
            return tuple.__getitem__(self, key)
        except TypeError:
            return object.__getattribute__(self, key) # calls descriptors


class Operation(object):
    quote = True

    def __init__(self, *args, **kwargs):
        # use kwargs so that connection cannot be supplied as an arg
        # defaults to global connection
        self._connection = kwargs.get("connection", connection)

        if self._connection is None:
            raise TypeError, "database connection not set"

        if self.quote:
            self._operation = self.__doc__
            self._parameters = args
        else:
            self._operation = self.__doc__ % args
            self._parameters = None

        many = kwargs.get("many")
        if many:
            self._parameters = many
            self.executefuncname = "executemany"
        else:
            self.executefuncname = "execute"

    @classmethod
    def _subclass_from_class(cls, ref_cls):
        """
        make a new subclass of cls with __doc__ from ref_cls and
        ref_cls in the name
        """
        cls_dict = dict(__doc__=ref_cls.__doc__)
        try:
            cls_dict["quote"] = ref_cls.quote
        except KeyError:
            pass

        return subclass(cls, cls_dict, ref_cls.__name__)

    @classmethod
    def _instance_from_class(cls, ref_cls, *args, **kwargs):
        subcls = cls._subclass_from_class(ref_cls)
        return subcls(*args, **kwargs)

    def cursor(self):
        return self._connection.cursor()

    def __call__(self):
        cursor = self.cursor()
        executefunc = getattr(cursor, self.executefuncname)
        executefunc(self._operation, self._parameters)

        return cursor


class ModifyOperation(Operation):
    def __new__(cls, *args, **kwargs):
        instance = Operation._instance_from_class(cls, *args, **kwargs)

        return instance()

class Create(ModifyOperation): pass


class Insert(ModifyOperation): pass


class Select(Operation):
    """
    calling returns an iterable operation
    """
    def __iter__(self):
        cursor, row_cls = self._cursor_and_row_cls()

        try:
            while True:
                yield row_cls(cursor.fetchone())
        except TypeError:
            pass

    def _cursor_and_row_cls(self):
        cursor = self()

        row_cls_dict = dict((column_description[0], _ordered_property(index))
                            for index, column_description
                            in enumerate(cursor.description))

        row_cls = subclass(Row, row_cls_dict, self.__class__.__name__)

        return cursor, row_cls


class SelectAll(Select, list):
    """
    instead of returning an object you can iterate over, this returns the whole
    table
    """
    def __new__(cls, *args, **kwargs):
        instance = Select._instance_from_class(cls, *args, **kwargs)

        cursor, row_cls = instance._cursor_and_row_cls()

        return map(row_cls, cursor.fetchall())


class SelectOneRow(Select, Row):
    def __new__(cls, *args, **kwargs):
        instance = Select._instance_from_class(cls, *args, **kwargs)

        try:
            return iter(instance).next()
        except StopIteration:
            return None


class SelectOneCell(SelectOneRow):
    def __new__(cls, *args, **kwargs):
        try:
            return SelectOneRow.__new__(cls, *args, **kwargs)[0]
        except TypeError:
            return None


class _MemoizeMetaclass(type):
    """
    ensures that MemoizeMixin is the first base
    """
    def __new__(cls, name, bases, dict):
        if name != "MemoizeMixin" and bases[0] is not MemoizeMixin:
            other_bases = tuple(base for base in bases
                                if base is not MemoizeMixin)
            bases = (MemoizeMixin,) + other_bases

        return type.__new__(cls, name, bases, dict)


class MemoizeMixin(object):
    """
    If you use mutable arguments or keyword arguments, then this
    mix-in cannot guarantee that the query will not be run.

    MemoizeMixin has a metaclass that ensures that its __new__ is called
    before any other base classes.
    """
    __metaclass__ = _MemoizeMetaclass

    def __new__(cls, *args, **kwargs):
        key = dumps((args, kwargs))
        try:
            cache = cls._cache
        except AttributeError:
            cache = cls._cache = {}

        if not key in cache:
            cache[key] = super(MemoizeMixin, cls).__new__(cls, *args, **kwargs)

        return cache[key]

def main(args):
    pass

if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
