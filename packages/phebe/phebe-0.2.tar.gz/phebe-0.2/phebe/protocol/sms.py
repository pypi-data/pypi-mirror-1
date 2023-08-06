# Copyright (c) 2006 Thomas Lotze
# See also LICENSE.txt

"""SMS-related AT commands.
"""

from phebe.connection import ATError
from phebe.response import parseResponse

RECEIVED_UNREAD = 0
RECEIVED_READ = 1
STORED_UNSENT = 2
STORED_SENT = 3
ALL_MESSAGES = 4


class SMSProtocol(object):
    """Implements SMS-related AT commands.
    """

    _conn = None

    def __init__(self, conn):
        self._conn = conn
        # make sure we're using PDU mode
        line = conn("+CMGF?", filter="+CMGF")[0]
        if parseResponse(line)[0] != 0:
            raise ATError("Phone won't use PDU mode for SM transmission.")

    def getStorages(self):
        line = self._conn("+CPMS=?", filter="+CPMS")[0]
        read, write, receive = parseResponse(line)
        return {"read": read,
                "write": write,
                "receive": receive}

    def getCurrent(self):
        line = self._conn("+CPMS?", filter="+CPMS")[0]
        response = parseResponse(line)
        result = {}
        for func in ("read", "write", "receive"):
            result[func] = {"mem": response.pop(0),
                            "used": response.pop(0),
                            "total": response.pop(0)}
        return result

    def setCurrent(self, read, *args):
        if len(args) > 2:
            raise ValueError("Too many storages given.")
        command = '+CPMS="%s"' % ','.join((read,) + args)
        line = self._conn(command, filter="+CPMS")[0]
        response = parseResponse(line)
        result = {}
        for func in ("read", "write", "receive"):
            result[func] = {"used": response.pop(0),
                            "total": response.pop(0)}
        return result

    def listMessages(self, stat=ALL_MESSAGES):
        lines = self._conn("+CMGL=%s" % stat, drop_empty=True)
        while lines:
            if len(lines) < 2 or not lines[0].startswith("+CMGL: "):
                raise ATError("Error reading message from phone response.")

            line = lines.pop(0)
            index, stat, alpha, length = parseResponse(line[7:])
            message = lines.pop(0)

            yield {"index": index,
                   "stat": stat,
                   "alpha": alpha,
                   "message": message,
                   }

    def readMessage(self, index):
        lines = self._conn("+CMGR=%s" % index, drop_empty=True)
        if len(lines) != 2 or not lines[0].startswith("+CMGR: "):
            raise ATError("Error reading message from phone response.")

        line, message = lines
        stat, alpha, length = parseResponse(line[7:])

        return {"stat": stat,
                "alpha": alpha,
                "message": message,
                }

    def delMessage(self, index):
        self._conn("+CMGD=%s" % index)
