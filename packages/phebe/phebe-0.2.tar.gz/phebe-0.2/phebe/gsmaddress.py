# Copyright (c) 2006-2008 Thomas Lotze
# See also LICENSE.txt

"""Adresses as defined by GSM 03.40.
"""

import phebe.gsmcoding


TYPE_UNKNOWN = 0
TYPE_INTERNATIONAL = 1
TYPE_NATIONAL = 2
TYPE_ALPHANUMERIC = 5

PLAN_UNKNOWN = 0
PLAN_ISDN = 1


def get_number_type(address_type):
    return {
        0: TYPE_UNKNOWN,
        1: TYPE_INTERNATIONAL,
        2: TYPE_NATIONAL,
        5: TYPE_ALPHANUMERIC,
        }.get(address_type >> 4 & 7)


def get_numbering_plan(address_type):
    return {
        0: PLAN_UNKNOWN,
        1: PLAN_ISDN,
        }.get(address_type & 15)


def get_address_type(number_type, numbering_plan):
    return (number_type & 7) << 4 + (numbering_plan or 0) & 15


def normalize(value, type):
    return (value[1:]
            if get_number_type(type) == TYPE_INTERNATIONAL
            and value.startswith('+')
            else value)


class GSMAddress(object):
    """Represents a typeful GSM address.
    """

    DEFAULT_PREFIX = None

    __all = {}

    __value = None
    value = property(lambda self: self.__value)

    __type = None
    type = property(lambda self: self.__type)

    __number_type = None
    number_type = property(lambda self: self.__number_type)

    __numbering_plan = None
    numbering_plan = property(lambda self: self.__numbering_plan)

    def __new__(cls, value, type):
        value = normalize(value, type)
        self = cls.__all.get((type, value))
        if self is None:
            self = cls.__all[(type, value)] = object.__new__(cls)
        return self

    def __init__(self, value, type):
        value = normalize(value, type)
        self.__value = value
        self.__type = type
        self.__number_type = get_number_type(type)
        if self.number_type in (
            TYPE_UNKNOWN, TYPE_INTERNATIONAL, TYPE_NATIONAL):
            self.__numbering_plan = get_numbering_plan(type)

    def __repr__(self):
        return "<GSM address of type %s: %s>" % (self.type, self.value)

    def __str__(self):
        return "%s: %s" % (self.type, self.value)

    def get_canonical(self, prefix=None):
        if self.number_type is TYPE_NATIONAL:
            assert self.value[0] == '0'
            if not prefix:
                prefix = GSMAddress.DEFAULT_PREFIX
            if prefix:
                return GSMAddress(prefix + self.value[1:],
                                  get_address_type(TYPE_INTERNATIONAL,
                                                   self.numbering_plan))
        return self


def gsm_address_from_octets(octets):
    """Read a gsm address from octets.

    Consumes those octets holding the address field.

    returns GSMAddress
    """
    address_len = octets.pop(0) # semi-octests excl. those with only fill bits
    address_type = octets.pop(0)

    address_len8 = (address_len + 1)/2 # ceil(int/2)
    address8 = octets[:address_len8]
    del octets[:address_len8]

    number_type = get_number_type(address_type)
    if number_type == TYPE_ALPHANUMERIC:
        address_len7 = address_len*4/7
        septets = phebe.gsmcoding.unpack_septets(address8)[:address_len7]
        number = phebe.gsmcoding.decode(septets)
    elif number_type in (TYPE_UNKNOWN, TYPE_NATIONAL, TYPE_INTERNATIONAL):
        number = "".join(str(o & 15) + str(o >> 4) for o in address8)
        number = number[:address_len]
    else:
        raise NotImplementedError("GSM number type: %s" % number_type)

    return GSMAddress(number, address_type)
