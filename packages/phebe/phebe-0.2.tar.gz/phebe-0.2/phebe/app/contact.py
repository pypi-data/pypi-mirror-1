# Copyright (c) 2006 Thomas Lotze
# See also LICENSE.txt

"""Phonebook functionality in terms of contacts.
"""

from phebe.protocol import phonebook


CONTACT_FIELDS = {'H': "home",
                  'W': "work",
                  'O': "other",
                  'M': "mobile",
                  'F': "fax",
                  }
FIELD_WIDTH = max(len(field) for field in CONTACT_FIELDS.itervalues())


class ContactList(dict):
    """Represents a phonebook storage's contents in terms of contacts.
    """

    _storage = None

    def __init__(self, storage):
        super(ContactList, self).__init__()

        self._storage = storage

    def __missing__(self, name):
        value = self[name] = Contact(name)
        return value

    def __repr__(self):
        return "<Contact list, %s entries>" % len(self)

    def synchronize(self):
        self._storage.synchronize()
        self.clear()

        for entry in self._storage:
            contact = self[entry.name]
            setattr(contact, CONTACT_FIELDS[entry.field], entry.number)

    def asConfig(self):
        return "\n".join(self[name].asConfig() for name in sorted(self))


class Contact(object):
    """Represents a phonebook contact with several numbers.
    """

    name = None

    home = None
    work = None
    other = None
    mobile = None
    fax = None

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return """<Contact "%s">""" % self.name.encode("ascii",
                                                       "backslashreplace")

    def asConfig(self):
        lines = ["[%s]" % self.name]
        for field in CONTACT_FIELDS.itervalues():
            number = getattr(self, field)
            if number:
                lines.append("%-*s %s" % (FIELD_WIDTH+1, field+":",
                                          number.value))
        lines.append("")
        return "\n".join(lines)
