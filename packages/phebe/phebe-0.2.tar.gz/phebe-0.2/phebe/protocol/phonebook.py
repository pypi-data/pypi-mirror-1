# Copyright (c) 2006-2008 Thomas Lotze
# See also LICENSE.txt

"""Phonebook-related AT commands.
"""

import phebe.rangelist
from phebe.response import parseResponse


class PhonebookProtocol(object):
    """Implements phonebook-related AT commands.
    """

    _conn = None
    _password = None

    def __init__(self, conn, password=None):
        self._conn = conn
        self._password = password

    def getStorages(self):
        line = self._conn("+CPBS=?", filter="+CPBS")[0]
        return parseResponse(line)[0]

    def getCurrent(self):
        line = self._conn("+CPBS?", filter="+CPBS")[0]
        return parseResponse(line)[0]

    def setCurrent(self, storage):
        command = '+CPBS="%s"' % storage
        if self._password:
            command += ',"%s"' % self._password
        self._conn(command)

    def getEntryParams(self):
        line = self._conn("+CPBW=?", filter="+CPBW")[0]
        indices, nlength, types, tlength = parseResponse(line)
        return {"indices": phebe.rangelist.RangeList(*indices),
                "nlength": nlength,
                "types": phebe.rangelist.RangeList(*types),
                "tlength": tlength,
                }

    def getEntry(self, index):
        line = self._conn("+CPBR=%s" % index, filter="+CPBR")[0]
        return parseEntry(line)

    def getEntries(self, first, last):
        return (parseEntry(line)
                for line in self._conn("+CPBR=%s,%s" % (first, last),
                                       filter="+CPBR")
                )

    def findEntries(self, search_text):
        return (parseEntry(line)
                for line in self._conn("+CPBF=%s" % search_text,
                                       filter="+CPBF")
                )

    def setEntry(self, number, type, name, field='H', index=""):
        self._conn('+CPBW=%s,"%s",%s,"%s/%s"' %
                   (index, number, type, name, field))

    def delEntry(self, index):
        self._conn('+CPBW=%s' % index)

    def changeName(self, index, new_name):
        self._conn('+CPBW=%s,,"%s"' % index, new_name)


FIELDS = {'H': u"Home",
          'W': u"Work",
          'O': u"Other",
          'M': u"Mobile",
          'F': u"FAX",
          }


def parseEntry(line):
    index, number, type, name = parseResponse(line)[:4]
    field = 'H'

    if isinstance(name, basestring):
        name_, sep, field_ = name.rpartition('/')
        if sep and field_ in ["H", "W", "O", "M", "F"]:
            name, field = name_, field_

    return {"index": index,
            "number": number,
            "type": type,
            "name": name,
            "field": field,
            }
