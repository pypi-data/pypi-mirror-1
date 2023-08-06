# -*- coding: utf-8 -*-
# Copyright (c) 2006-2008 Thomas Lotze
# See also LICENSE.txt

"""GSM alphabet decoding.

Using GSM standard 3GPP TS 03.40, version 7.5.0, release 1998.
"""


GSM_DEFAULT_TABLE = u"\
@£$¥èéùìòÇ\nØø\rÅå\
Δ_ΦΓΛΩΠΨΣΘΞ ÆæßÉ\
 !\"#¤%&'()*+,-./\
0123456789:;<=>?\
¡ABCDEFGHIJKLMNO\
PQRSTUVWXYZÄÖÑÜ§\
¿abcdefghijklmno\
pqrstuvwxyzäöñüà\
"

class FallbackDict(dict):

    def __init__(self, fallback, *args, **kwargs):
        super(FallbackDict, self).__init__(*args, **kwargs)
        self.__fallback = fallback

    def __missing__(self, key):
        return self.__fallback[key]


GSM_EXTENSION_TABLE = FallbackDict(GSM_DEFAULT_TABLE, {
    10: u"\f",
    20: u"^",
    27: u" ",
    40: u"{",
    41: u"}",
    47: u"\\",
    60: u"[",
    61: u"~",
    62: u"]",
    64: u"|",
    101: u"€",
    })


def unpack_septets(octets):
    """Decode 7 bit character strings packed into 8 bit byte strings.

    input: iterable of int

    returns str
    """
    septets = []
    overflow = overflow_len = 0

    for value in octets:
        septets.append(value << overflow_len & 127 | overflow)
        overflow = value >> (7 - overflow_len)
        overflow_len += 1
        if overflow_len == 7:
            septets.append(overflow)
            overflow = overflow_len = 0

    return septets


def decode(septets):
    """Decode septets to unicode by the GSM default alphabet.

    septets: iterable of int

    returns unicode
    """
    septets_iter = iter(septets)
    return u"".join(GSM_DEFAULT_TABLE[s] if s != 27
                    else GSM_EXTENSION_TABLE[septets_iter.next()]
                    for s in septets_iter)
