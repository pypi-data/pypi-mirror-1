# Copyright (c) 2006-2008 Thomas Lotze
# See also LICENSE.txt

"""Generic setup stuff for scripts exercising phebe.
"""

import os
import sys
import optparse
import ConfigParser

import phebe.connection
import phebe.gsmaddress


class ScriptSupport(object):
    """Generic initializer for phebe scripts.
    """

    options = None
    args = None
    connection = None
    must_encode = None

    def __init__(self):
        self.option_parser = optparse.OptionParser()
        self.add_option = self.option_parser.add_option
        self.config = ConfigParser.ConfigParser()

        self.add_option("-d", "--device")
        self.add_option("-b", "--baud-rate", type="int")
        self.add_option("-p", "--prefix")

    def initialize(self, verbose=False):
        self.config.read(("/etc/pheberc",
                          os.path.expanduser("~/.pheberc")))
        self.options, self.args = self.option_parser.parse_args()

        connection_config = (dict(self.config.items("Connection"))
                             if self.config.has_section("Connection")
                             else {})
        if verbose:
            print "Connecting..."
        try:
            self.connection = phebe.connection.Connection(
                self.options.device or connection_config.get("device"),
                self.options.baud_rate or connection_config.get("baud_rate"))
        except (ValueError, IOError, phebe.connection.ATError), e:
            print >>sys.stderr, str(e)
            sys.exit(1)

        self.must_encode = not sys.stdout.isatty()

        local_config = (dict(self.config.items("Local"))
                        if self.config.has_section("Local")
                        else {})

        phebe.gsmaddress.GSMAddress.DEFAULT_PREFIX = \
            self.options.prefix or local_config.get("prefix")

    def out(self, value):
        """Print to stdout, encode if necessary.

        value: something that has a unicode representation
        """
        if self.must_encode:
            print unicode(value).encode("utf-8", "backslashreplace")
        else:
            print unicode(value)


scriptsupport = ScriptSupport()
