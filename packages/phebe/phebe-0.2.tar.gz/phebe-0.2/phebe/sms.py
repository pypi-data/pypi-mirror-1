# Copyright (c) 2006-2008 Thomas Lotze
# See also LICENSE.txt

"""SMS representation and PDU decoder.

Using GSM standard 3GPP TS 03.40, version 7.5.0, release 1998
and protocol description at <http://www.dreamfabric.com/sms/>.
"""

import datetime
import codecs

import phebe.gsmcoding
import phebe.gsmaddress


hex_decoder = codecs.getdecoder("hex_codec")
utf_16_decoder = codecs.getdecoder("utf_16")

DEFAULT_ALPHABET = 0
EIGHT_BIT = 1
UCS2 = 2


class ShortMessage(object):
    """Represents a generic GSM short message.
    """

    pdu_type = "generic"

    pdu = None
    address = None
    datetime = None
    header = None
    user_data = None

    def __init__(self, pdu=""):
        self.pdu = pdu

    def __repr__(self):
        return "<Short message of type %s: %r>" % (self.pdu_type,
                                                   self.user_data)

    def user_data_from_octets(self, flags, octets, coding_scheme):
        user_data_len = octets.pop(0)

        if flags & 64: # user data header indicator
            header_len8 = octets[0] + 1
            self.header = octets[1:header_len8]
        else:
            header_len8 = 0

        compressed = (coding_scheme & 224 == 32)

        if (coding_scheme & 236 == 0 # general data coding
            or coding_scheme & 224 == 192 # message waiting indication
            or coding_scheme & 244 == 240): # data coding/message class
            coding = DEFAULT_ALPHABET
        elif (coding_scheme & 236 == 4 # general data coding
              or coding_scheme & 244 == 244): # data coding/message class
            coding = EIGHT_BIT
        elif (coding_scheme & 236 == 8 # general data coding
              or coding_scheme & 240 == 224): # message waiting indication
            coding = UCS2
        else:
            raise ValueError("Unsupported coding scheme.")

        if coding == DEFAULT_ALPHABET and not compressed:
            header_len7 = (header_len8*8 + 6)/7 # ceil(int*8/7)
            septets = phebe.gsmcoding.unpack_septets(octets)
            septets = septets[header_len7:user_data_len]
            self.user_data = phebe.gsmcoding.decode(septets)
        else:
            octets = octets[header_len8:user_data_len]

            if compressed:
                raise NotImplementedError

            if coding == DEFAULT_ALPHABET:
                septets = phebe.gsmcoding.unpack_septets(octets)
                self.user_data = phebe.gsmcoding.decode(septets)
            else:
                user_data = "".join(chr(o) for o in octets)
                if coding == UCS2:
                    user_data = utf_16_decoder(user_data)
                self.user_data = user_data


class ShortMessageDeliver(ShortMessage):
    """Represents a short message of PDU type DELIVER.
    """

    pdu_type = "DELIVER"

    def protocol_data_from_octets(self, flags, octets):
        self.address = phebe.gsmaddress.gsm_address_from_octets(octets)
        del octets[0] # protocol identifier
        coding_scheme = octets.pop(0)
        self.datetime = datetime_from_octets(octets)

        return coding_scheme

    def dump(self):
        return """\
Sender: %s
Date: %s

%s
""" % (self.address, self.datetime, self.user_data)


class ShortMessageSubmit(ShortMessage):
    """Represents a short message of PDU type SUBMIT.
    """

    pdu_type = "SUBMIT"

    def protocol_data_from_octets(self, flags, octets):
        del octets[0] # TP message reference
        self.address = phebe.gsmaddress.gsm_address_from_octets(octets)
        del octets[0] # protocol identifier
        coding_scheme = octets.pop(0)

        # TP validity period
        if flags & 8: # enhanced or absolute format
            del octets[:7]
        elif flags & 16: # relative format
            del octets[0]

        return coding_scheme

    def dump(self):
        return """\
Recipient: %s
""" % self.address + ("""Date: %s
""" % self.datetime if self.datetime else "") + """\

%s
""" % self.user_data


def short_message(pdu):
    """Factory for short message objects.

    pdu: PDU formatted message

    returns an instance of a ShortMessage subclass
    """
    octets = [ord(c) for c in hex_decoder(pdu)[0]]

    smsc_len = octets.pop(0)
    del octets[0] # smsc address type
    del octets[:smsc_len-1] # smsc address

    flags = octets.pop(0)

    cls = {0: ShortMessageDeliver,
           1: ShortMessageSubmit,
           }[flags & 3] # message type indicator
    obj = cls(pdu)

    coding_scheme = obj.protocol_data_from_octets(flags, octets)
    obj.user_data_from_octets(flags, octets, coding_scheme)

    return obj


def datetime_from_octets(octets):
    """Read date and time from octets.

    Consumes those octets holding the timestamp.

    returns naive datetime.datetime instance relative to UTC
    """
    values = [(o&15)*10 + (o>>4) for o in octets[:7]]
    del octets[:7]
    year = values[0]
    result = datetime.datetime(year if year > 68 else year+2000, *values[1:6])
    zone = values[-1]
    delta = datetime.timedelta(minutes=(zone&127)*15)
    if zone & 128:
        result -= delta
    else:
        result += delta
    return result
