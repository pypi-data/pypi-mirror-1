# Copyright (c) 2006-2008 Thomas Lotze
# See also LICENSE.txt

"""Basic communication using AT commands on a serial device.
"""

import sys
import termios


class ATError(Exception):
    """Raised on an error response from the phone.
    """


class Connection(object):
    """Represents a mobile phone on a serial device.

    Sends raw AT commands, yields response lines, raises exceptions on errors.
    """

    device = None

    def __init__(self, device_str, rate_str):
        try:
            rate = getattr(termios, "B%s" % rate_str)
        except AttributeError:
            raise ValueError("Invalid BAUD rate.")

        self.device = open(device_str, "r+")

        tcattrs = termios.tcgetattr(self.device)
        tcattrs[4] = tcattrs[5] = rate # in and out speed
        termios.tcsetattr(self.device, termios.TCSANOW, tcattrs)

        self.check()
        self("E0", "switching off command echo")
        self('+CSCS="UTF-8"', "setting charset to UTF-8")

    def __call__(self, command, info=None, filter=None, drop_empty=False):
        """Send a command to the phone.

        command: unicode, complete command without the leading "AT"
        info: unicode, comment describing the command

        returns list of unicode (response lines)
        """
        self.device.write("AT%s\r\n" % command.encode("utf-8"))

        cmd_desc = u"'AT%s'" % command
        if info:
            cmd_desc += u" (%s)" % info

        result = []
        while True:
            line = self.device.readline()
            try:
                line = line.decode("utf-8")
            except UnicodeDecodeError:
                raise ATError("Error decoding response from %s" % cmd_desc)

            line = line.strip()
            if line == "OK":
                break
            if "ERROR" in line:
                raise ATError("""Error on %s:\n%s""" % (cmd_desc, line))

            if filter:
                prefix, sep, line = line.partition(": ")
                if prefix == filter and sep:
                    result.append(line)
            else:
                if line or not drop_empty:
                    result.append(line)

        return result

    def check(self):
        """Check for presence of and communication with a phone.
        """
        self("", "checking for a phone")


def atterm(conn):
    error_handling = conn("+CMEE?", filter="+CMEE")[0]
    conn("+CMEE=2", "switching on verbose error codes")
    try:
        while True:
            command = raw_input("(AT) ").strip().decode(
                sys.stdin.encoding or "ascii").upper()
            if command == "EOF":
                break
            if command.startswith("AT"):
                command = command[2:]
            try:
                for line in conn(command):
                    if line:
                        print line
            except ATError, e:
                print >>sys.stderr, e.args[0].encode(
                    sys.stderr.encoding or "ascii", "backslashreplace")
    except EOFError:
        print
    conn("+CMEE=" + error_handling, "resetting error codes")
