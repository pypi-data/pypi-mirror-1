# Copyright (c) 2008 Thomas Lotze
# See also LICENSE.txt

"""Command shell to exercise phebe interactively.
"""

import functools
import cStringIO as StringIO

import tl.cli.page
import tl.cmd
import tl.readline

import phebe.connection
import phebe.proxy.phonebook
import phebe.proxy.sms
import phebe.app.contact
import phebe.app.message
import phebe.rangelist
import phebe.scriptsupport


def page_or_redirect(func):
    @functools.wraps(func)
    def wrapper(self, line):
        words = line.split()
        args = []
        while words:
            word = words.pop(0)
            if word == ">":
                filename = words.pop(0)
                break
            if word.startswith(">"):
                filename = word[1:]
                break
            args.append(word)
        else:
            filename = None

        if filename is None:
            stream = StringIO.StringIO()
        else:
            stream = open(filename, "w")

        def out(value=""):
            text = unicode(value).encode("utf-8", "backslashreplace")
            stream.write(text + "\n")

        func(self, out, " ".join(args + words))

        if filename is None:
            tl.cli.page.page(stream.getvalue())
        stream.close()

    return wrapper


class Shell(tl.cmd.Cmd):
    """Command shell to exercise phebe interactively.
    """

    def __init__(self):
        tl.cmd.Cmd.__init__(self)
        self.script = phebe.scriptsupport.scriptsupport
        self.last_dumped_messages = []
        self.last_dumped_conversations = []

    def initialize(self):
        self.script.initialize(verbose=True)
        self.conn = self.script.connection
        for line in self.conn("I", "requesting identification information"):
            if line:
                print line
        print

    _phonebook = None
    @property
    def phonebook(self):
        if self._phonebook is None:
            self._phonebook = phebe.proxy.phonebook.Phonebook(self.conn)
            self._phonebook.synchronize()
        return self._phonebook

    _sms = None
    @property
    def sms(self):
        if self._sms is None:
            self._sms = phebe.proxy.sms.SMSMobileStation(self.conn)
            self._sms.synchronize_stats()
        return self._sms

    _msg_box = None
    @property
    def msg_box(self):
        if self._msg_box is None:
            self.sms.ME.synchronize()
            self._msg_box = phebe.app.message.MessageBox(
                [self.sms.ME], phonebook=self.phonebook)
        return self._msg_box

    @tl.readline.with_history("atterm")
    def do_atterm(self, line):
        """Issue AT commands interactively.

        The letters "AT" will be prepended if omitted from your commands.

        Exit by sending the end-of-file signal or typing "EOF".
        """
        print
        phebe.connection.atterm(self.conn)

    def do_usage(self, line):
        """Display usage statistics of the phone's storages.
        """
        for name, pb_storage in self.phonebook.iteritems():
            if pb_storage.indices:
                print ("Phonebook storage %s: %s/%s entries" %
                       (name, len(pb_storage), len(pb_storage.indices)))
        for sms_storage in self.sms.SM, self.sms.ME:
            print ("SMS storage %s: %s/%s messages" %
                   (sms_storage.name, sms_storage.used, sms_storage.total))

    def do_smsusage(self, line):
        """Show short messages stored on the phone.
        """
        for name, conversation in sorted(self.msg_box.iteritems()):
            print "%s: %s" % (name, len(conversation))

    def phonebook_listing(func):
        @functools.wraps(func)
        def wrapper(self, out, line):
            names = line.split() or ["ME"]
            for name in names:
                if len(names) > 1:
                    out()
                    out("# " + name)
                    out()
                func(self, out, name)
        return wrapper

    @page_or_redirect
    @phonebook_listing
    def do_phonebook(self, out, name):
        """List phonebook entries using a pager.

        Phonebook names may be given as command arguments (default: ME).
        The output may be sent to a file using > as in system shells.
        """
        for entry in self.phonebook[name]:
            out(entry)

    @page_or_redirect
    @phonebook_listing
    def do_contacts(self, out, name):
        """List contacts from the phonebook using a pager.

        Phonebook names may be given as command arguments (default: ME).
        The output may be sent to a file using > as in system shells.
        """
        contacts = phebe.app.contact.ContactList(self.phonebook[name])
        contacts.synchronize()
        out(contacts.asConfig())

    @page_or_redirect
    def do_messages(self, out, line):
        """Dump messages found in the ME SMS storage.

        Message indexes and ranges may be listed as command arguments
        (default: dump all messages).
        The output may be sent to a file using > as in system shells.
        """
        self.sms.ME.synchronize()
        phebe.app.message.resolve_names(self.sms.ME.itervalues(),
                                        self.phonebook)
        data = self.sms.ME.iteritems()
        if line:
            ranges = phebe.rangelist.range_list(line.split(),
                                                self.sms.ME.total)
            data = ((index, msg) for index, msg in data if index in ranges)
        del self.last_dumped_messages[:]
        for key, value in sorted(data):
            out("[%s]\n%s" % (key, value.dump()))
            self.last_dumped_messages.append(key)
        out("(%s messages)\n" % len(self.last_dumped_messages))

    @page_or_redirect
    def do_conversations(self, out, line):
        """Dump conversations found in the ME SMS storage.

        Partial names of contacts may be listed as command arguments
        (default: dump all conversations).
        The output may be sent to a file using > as in system shells.
        """
        data = self.msg_box.iteritems()
        if line:
            data = ((name, conversation) for name, conversation in data
                    if any(arg in name for arg in line.split()))
        data = sorted(data)
        del self.last_dumped_conversations[:]
        for name, value in data:
            out("[%s (%s messages)]\n\n%s\n" % (
                name, len(value), value.dump()))
            self.last_dumped_conversations.append(name)
        out("(%s conversations)\n" % len(self.last_dumped_conversations))

    def do_deletemessages(self, line):
        """Delete messages from the ME SMS storage.

        Message indexes and ranges may be listed as command arguments
        (default: delete all messages).
        """
        self.do_messages(line)
        if tl.readline.input("Delete? (yes/no) ") != "yes":
            return
        for index in self.last_dumped_messages:
            del self.sms.ME[index]

    def do_deleteconversations(self, line):
        """Delete conversations from the ME SMS storage.

        Partial names of contacts may be listed as command arguments
        (default: delete all conversations).
        """
        self.do_conversations(line)
        if tl.readline.input("Delete? (yes/no) ") != "yes":
            return
        for name in self.last_dumped_conversations:
            self.msg_box.delete(name)


def shell():
    """Phebe shell.

    Runs the interactive text UI.
    """
    p = Shell()
    p.do_help(None)
    p.initialize()
    p.cmdloop()
