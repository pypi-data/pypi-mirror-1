# Copyright (c) 2006 Thomas Lotze
# See also LICENSE.txt

"""SMS functionality in terms of messages.
"""

from functools import wraps

from phebe import connection, sms
from phebe.protocol import sms as smsprotocol


class SMSMobileStation(object):
    """Represents a phone as a mobile station in terms of message storages.
    """

    _conn = None
    _protocol = None

    ME = None
    SM = None

    def __init__(self, conn):
        super(SMSMobileStation, self).__init__()

        self._protocol = smsprotocol.SMSProtocol(conn)

        self.ME = MessageStorage(self._protocol, "ME")
        self.SM = MessageStorage(self._protocol, "SM")

    def __repr__(self):
        return "<SMS mobile station, ME: %s/%s, SM: %s/%s>" % (
            len(self.ME),
            self.ME.total if self.ME.total is not None else "n/a",
            len(self.SM),
            self.SM.total if self.SM.total is not None else "n/a",)

    def synchronize(self):
        self.ME.synchronize()
        self.SM.synchronize()

    def synchronize_stats(self):
        self.ME.synchronize_stats()
        self.SM.synchronize_stats()


def current(meth):
    """Decorator for MessageStorage methods.

    Ensures that the phone's current preferred storage for reading is set to
    the one represented by this MessageStorage (self).

    Updates the _info dict describing used and total message count.
    """
    @wraps(meth)
    def decorated(self, *args, **kwargs):
        if not self._cur_depth:
            info = self._protocol.setCurrent(self.name)
            self._info = info["read"]
            assert self._protocol.getCurrent()["read"]["mem"] == self.name
        self._cur_depth += 1
        try:
            result = meth(self, *args, **kwargs)
        finally:
            self._cur_depth -= 1
        return result
    return decorated


class MessageStorage(dict):
    """Represents an SMS message storage holding indexed messages.
    """

    _protocol = None
    name = None

    _info = None # set by the "current" decorator
    _cur_depth = 0 # used by the "current" decorator

    used = None
    total = None

    def __init__(self, protocol, name):
        super(MessageStorage, self).__init__()
        self._protocol = protocol
        self.name = name

    def __repr__(self):
        return "<SMS message storage %s: %s/%s>" % (
            self.name, len(self),
            self.total if self.total is not None else "n/a")

    @current
    def synchronize(self):
        self.synchronize_stats()
        self.clear()
        for record in self._protocol.listMessages():
            record["storage"] = self
            record["message"] = sms.short_message(record["message"])
            self[record["index"]] = Message(**record)
        assert len(self) == self.used

    @current
    def synchronize_stats(self):
        self.used = self._info["used"]
        self.total = self._info["total"]

    @current
    def __delitem__(self, index):
        super(MessageStorage, self).__delitem__(index)
        self._protocol.delMessage(index)

    def dump(self):
        return "\n\n".join("[%s]\n%s" % (index, self[index].dump())
                           for index in sorted(self))


class Message(object):
    """Represents an SMS message stored in a phone.
    """

    message = None

    storage = None
    storage_name = None
    index = None
    stat = None
    alpha = None

    annotation_names = {}
    annotations = None

    def __init__(self, storage=None, storage_name=None, index=None, stat=None,
                 alpha=None, message=None):
        self.storage = storage
        self.storage_name = storage_name
        self.index = index
        self.stat = stat
        self.alpha = alpha
        self.message = message

        if not storage_name and storage:
            self.storage_name = storage.name

        self.annotations = {}

    def __repr__(self):
        return "<Short message %s[%s]>" % (self.storage_name, self.index)

    def dump(self, show=True, hide=()):
        if show is True:
            annotations = set(self.annotations)
        elif show:
            annotations = set(show)
        else:
            annotations = set()
        annotations.difference_update(hide)

        return "".join("%s: %s\n" % (Message.annotation_names.get(key, key),
                                     self.annotations[key])
                       for key in sorted(annotations)) + self.message.dump()

    def delete(self):
        # Since this is a proxy class, this method should really be __del__.
        # However, we don't want the phone to be operated depending on the gc.
        del self.storage[self.index]
        self.storage = self.index = None
