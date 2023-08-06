# Copyright (c) 2006-2007 Thomas Lotze
# See also LICENSE.txt

"""Phonebook functionality in terms of single entries.
"""

from collections import defaultdict
from functools import wraps

from phebe import connection, gsmaddress
from phebe.protocol import phonebook


class Phonebook(dict):
    """Represents a phone's phonebook in terms of named storages.
    """

    _conn = None

    _lookup = None

    def __init__(self, conn, password=None):
        super(Phonebook, self).__init__()

        self._pb = phonebook.PhonebookProtocol(conn, password)

        for name in self._pb.getStorages():
            self[name] = PhonebookStorage(self._pb, name)

        self._lookup = {}

    def __repr__(self):
        return "<Phonebook %s>" % dict(
            (str(key), len(value) if value.indices is not None else "n/a")
            for key, value in self.iteritems())

    def synchronize(self):
        self._lookup.clear()
        for storage in self.values():
            try:
                storage.synchronize()
                self._lookup.update(storage._lookup)
            except connection.ATError:
                pass

    def lookup(self, obj):
        entry = self._lookup.get(obj)
        if not entry and isinstance(obj, gsmaddress.GSMAddress):
            entry = self._lookup.get(obj.get_canonical())
        return entry


def current(meth):
    """Decorator for PhonebookStorage methods.

    Ensures that the phone's current storage is set to the one represented by
    this PhonebookStorage (self).
    """
    @wraps(meth)
    def decorated(self, *args, **kwargs):
        self._pb.setCurrent(self.name)
        assert self._pb.getCurrent() == self.name
        return meth(self, *args, **kwargs)
    return decorated


class PhonebookStorage(list):
    """Represents a phone book storage holding a sequence of entries.
    """

    _pb = None
    name = None

    indices = None
    nlength = None
    types = None
    tlength = None

    _lookup = None

    def __init__(self, pb, name):
        super(PhonebookStorage, self).__init__()
        self._pb = pb
        self.name = name
        self._lookup = defaultdict(dict)

    def __repr__(self):
        return "<Phonebook storage %s, %s>" % (
            self.name,
            "%s entries" % len(self)
            if self.indices is not None else "unsynchronized")

    @current
    def synchronize(self):
        if self.name == "MV":
            return

        params = self._pb.getEntryParams()
        self.indices = params["indices"]
        self.nlength = params["nlength"]
        self.types = params["types"]
        self.tlength = params["tlength"]

        first = min(self.indices)
        last = max(self.indices)
        self[:] = (PhonebookEntry(self, **entry_dict)
                   for entry_dict in self._pb.getEntries(first, last))

        self._lookup.clear()
        for entry in self:
            self._lookup[entry.number] = entry
            self._lookup.setdefault(entry.number.get_canonical(), entry)
            self._lookup[(entry.name, entry.field)] = entry
            self._lookup[entry.name][entry.field] = entry


class PhonebookEntry(object):
    """Represents a single phonebook entry.
    """

    storage = None

    index = None
    number = None
    name = None
    field = None

    def __init__(self, storage,
                 index=None, number=None, type=None, name=None, field='H'):
        self.storage = storage

        self.index = index
        self.number = gsmaddress.GSMAddress(number, type)
        self.name = name
        self.field = field

    def __repr__(self):
        return "[%*s] %s @%s: %s" % (
            len(str(max(self.storage.indices))), self.index,
            self.name.encode("ascii", "backslashreplace"),
            phonebook.FIELDS[self.field], self.number.value)

    def __unicode__(self):
        return u"[%*s] %s @%s: %s" % (
            len(str(max(self.storage.indices))), self.index,
            self.name, phonebook.FIELDS[self.field], self.number.value)
