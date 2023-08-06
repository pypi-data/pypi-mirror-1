=====
Phebe
=====

Communicate with a mobile phone connected to your computer.

Phebe contains a command shell that performs common tasks on a phone connected
to your computer: get usage stats, back-up the phonebook and contacts, as well
as download and delete short messages. Communication is done through AT
commands as specified by Sony-Ericsson.

This package requires Python 2.5 or newer.


The command shell
=================

Configuration
-------------

The ``phebe`` shell needs to be told the device node that represents the phone
to the operating system, and the BAUD rate the phone communicates at. These
may be given in an ini-style configuration file, either system-wide at
``/etc/pheberc`` or in the user's home directory at ``~/.pheberc``, or as
command line options.

Command line options override configuration files, and ``~/.pheberc``
overrides ``/etc/pheberc``. If any of device node and baud rate is not
specified in one of the configuration files, it must be given on the command
line. No useful default values are provided for these two settings.

Another option is the default national phone number prefix. This allows
dealing with numbers that sometimes appear in national format and sometimes in
international format, e.g. when looking up short message addresses in the
phonebook. This option is not required.

A sample configuration file might look like this::

  [Connection]
  device=/dev/ttyACM0
  baud=9600

  [Local]
  # Germany
  prefix=49

The corresponding command line options are defined as follows:

--help, -h                           show this help message and exit

--device=DEVICE, -d DEVICE           the device node

--baud-rate=BAUD_RATE, -b BAUD_RATE  the BAUD rate

--prefix=PREFIX, -p PREFIX           the default national phone number prefix

The information from the above configuration file might be specified in terms
of command line options like this::

  $ phebe --device=/dev/ttyACM0 --baud-rate=9600 --prefix=49

Usage
-----

The following is a short description of what the commands provided by the
``phebe`` shell do and what their arguments mean.

``atterm``
  Talk to your phone by issuing AT commands at a prompt and receiving the raw
  textual response from the device.

``usage``
  Prints a summary of how much of your phone's resources are used. This
  currently includes the used vs total number of entries in each of the
  phonebooks and SMS storages.

``smsusage``
  Prints the total number of stored short messages per contact (received plus
  sent).

``phonebook``
  Lists all entries from the phonebook storages named as command arguments, in
  the order they are indexed by the phone. Without arguments, lists the "ME"
  storage.

``contacts``
  Lists entries grouped by contact, per storage. The output format is roughly
  ini-style.

``messages``
  Lists short messages from the "ME" SMS storage.

  Arguments may be either storage indexes or index ranges (such as "14-23") of
  single messages to list. Without arguments, all messages are listed. If
  non-existent indexes are given explicitly or included in ranges given, they
  will be ignored.

``conversations``
  Lists short messages from the "ME" SMS storage grouped into conversations
  with your contacts.

  Arguments may be partial names; conversations with any matching contacts are
  listed. Without arguments, all conversations are listed. If a sender or
  recipient number cannot be resolved into a contact name using the phonebook,
  the number itself is used for the grouping.

``deletemessages``
  Deletes short messages from your phone's "ME" SMS storage.

  Command arguments are the same as for the ``messages`` command. Messages to
  be deleted will be listed first and deletion is guarded by a safety query.

``deleteconversations``
  Deletes short messages belonging to conversations with your contacts from
  your phone's "ME" SMS storage.

  Command arguments are the same as for the ``conversations`` command.
  Messages to be deleted will be listed first and deletion is guarded by a
  safety query.

The ``phonebook``, ``contacts``, ``messages`` and ``conversations`` commands
send their output to the default pager for convenient browsing. You can
redirect the output to a file instead using the ``>`` operator known from
system shells. To send a phonebook dump to a file instead of paging through
it, for example, say::

  (Cmd) phonebook > /tmp/phonebook.backup


The Phebe API
=============

This section contains an overview of Phebe's concepts and package structure.

The connection
--------------

Phebe talks to a mobile phone by sending AT commands to a device node and
reading a textual response from it, which may or may not signal an error.

The connection object encapsulates device-level communication with the phone.
It is the only object which cares about the device node name and the BAUD
rate. To the rest of the application, it is a callable that takes an AT
command string as a parameter and either returns a sequence of respose lines
or raises an exception. It does not maintain any state.

Protocols
---------

Each functionality of the phone, such as phonebook or SMS management, has its
own group of AT commands with specified parameters and result formats.

A protocol is an object whose interface to the rest of the application
reflects the actions related to a specific functionality. These actions
directly correspond to what is implemented by the phone as AT commands.
Protocols use the connection object to send AT commands with appropriately
formatted parameters, receive and interpret the response, and return plain
Python data structures holding the received information. They don't maintain
any state, either.

Proxies
-------

As opposed to the stateless, action-related protocols, proxies represent
particular aspects of the phone's functionality and state to the application.

A proxy employs a protocol object and exposes an interface that is defined by
the demands of the functionality modelled. Proxies are stateful; their state
represents the information stored on and the current state of the phone. They
may need to be explicitly synchronized against the phone. Modifying a proxy's
state immediately modifies the information stored in or the state of the
phone. It is probably a good idea to use at most one proxy per phone for any
given functionality at a time.

Application objects
-------------------

Application objects are Phebe's highest-level objects representing the phone.
They combine various functionalities independent of the command specification.

Application objects expose whatever interface fits their purpose. They define
and use Phebe-specific data structures. Each application object may make use
of any number of different proxies simultaneously. Manipulating an application
object's state should not directly affect the phone; the phone should rathter
be modified explicitly through methods. This is so that application objects
may be used more freely.

Package structure
-----------------

The phebe package contains three subpackages and a number of modules, all of
them described in the following.

``connection``
  the fundamental Connection class and the ATError exception

``rangelist``
  the RangeList data type used for specifying message index ranges

``response``
  parsing responses to AT commands

``gsmcoding``
  handling PDUs encoded with the GSM alphabet and 7-bit packed

``gsmaddress``
  a phone number implementation aware of number types and numbering plans

``sms``
  data structures for various SMS types as defined by the GSM standards

``shell``
  the ``phebe`` command shell and its egg entry point

``phebe.protocol``

    ``phonebook``
      access to the phonebook

    ``sms``
      access to the SMS storages

``phebe.proxy``

    ``phonebook``
      proxy representing the phone's phonebook

    ``sms``
      proxy representing the phone as an SMS mobile station

``phebe.app``

    ``contact``
      manage any contact information stored on the phone

    ``message``
      manage any messaging done through the phone using contacts


Status
======

The implementation follows the Sony-Ericsson developer guidelines for using AT
commands as of December 7, 2006, see
<http://developer.sonyericsson.com/getDocument.do?docId=65054>. It has been
tested only on a SE K750i, using Debian and Gentoo Linux distributions with a
2.6 kernel so far.

The current status of Phebe is "works for me", i.e. it provides the
functionality the author immediately needs: get usage stats of the phone,
back-up the phonebook, dump and delete short messages. See ROADMAP.txt and
TODO.txt for prospective further developments.

While neither talking through the AT command interface nor the higher-level
data structures implemented by Phebe are operating system specific,
communication with the device is. Phebe currently does this by using a Python
module only available on Unix. The author is not going to port Phebe to
non-Unix systems any time soon, so if you want it to support your OS, you have
to supply an appropriate patch.


Contact
=======

Phebe is written by Thomas Lotze. Please contact the author at
<thomas@thomas-lotze.de> to provide feedback or suggestions on or
contributions to Phebe.

See also <http://www.thomas-lotze.de/en/software/phebe/>.


.. Local Variables:
.. mode: rst
.. End:
