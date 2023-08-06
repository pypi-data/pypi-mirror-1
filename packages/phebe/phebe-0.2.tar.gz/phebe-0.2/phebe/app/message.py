# Copyright (c) 2006-2008 Thomas Lotze
# See also LICENSE.txt

"""Message (SMS etc) management.
"""

from phebe.proxy import phonebook, sms


class MessageBox(dict):
    """Container for conversations per contact name.
    """

    _storages = None
    _phonebook = None

    def __init__(self, storages, phonebook=None):
        super(MessageBox, self).__init__()

        self._storages = storages
        self._phonebook = phonebook
        self.build()

    def __missing__(self, name):
        value = self[name] = Conversation(name)
        return value

    def __repr__(self):
        return "<Message box, %s conversations, %s messages>" % (
            len(self), sum(len(group) for group in self.itervalues()))

    def synchronize(self):
        if self._phonebook:
            self._phonebook.synchronize()
        for storage in self._storages:
            storage.synchronize()
        self.clear()
        self.build()

    def build(self):
        for storage in self._storages:
            if self._phonebook:
                resolve_names(storage.itervalues(), self._phonebook)
            for index, msg in storage.iteritems():
                self[msg.annotations.get("contact_name") or
                     str(msg.message.address)].append(msg)

    def delete(self, name):
        self[name].delete_all()
        del self[name]

    def dump(self):
        return "\n\n".join("[%s]\n\n%s" % (name, self[name].dump())
                         for name in sorted(self))


def create_messagebox_me(device_str, rate_str):
    import phebe.connection
    import phebe.proxy.sms
    import phebe.proxy.phonebook

    conn = phebe.connection.Connection(device_str, rate_str)
    sms = phebe.proxy.sms.SMSMobileStation(conn)
    pb = phebe.proxy.phonebook.Phonebook(conn)

    return MessageBox([sms.ME], phonebook=pb)


class Conversation(list):
    """Container for messages out of indexed storages, sorted by date.
    """

    name = None

    def __init__(self, name):
        super(Conversation, self).__init__()

        self.name = name

    def __repr__(self):
        return '<Conversation with "%s", %s messages>' % (
            self.name, len(self))

    def append(self, msg):
        super(Conversation, self).append(msg)
        self.sort(cmp=lambda a, b:
                  -1 if not a.message.datetime else
                  1 if not b.message.datetime else
                  cmp(a.message.datetime, b.message.datetime))

    def delete(self, index):
        self[index].delete()
        del self[index]

    def delete_all(self):
        for msg in self:
            msg.delete()
        del self[:]

    def dump(self):
        return "\n\n".join(msg.dump(hide=["contact_name"]) for msg in self)


def resolve_names(messages, phonebook):
    sms.Message.annotation_names["contact_name"] = "Contact name"
    for msg in messages:
        pb_entry = phonebook.lookup(msg.message.address)
        if pb_entry:
            msg.annotations["contact_name"] = pb_entry.name
