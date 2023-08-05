#!/usr/bin/env python

"""
Talk to a T616/T610 via a serial connection and make it do various things.

For Bluetooth under Linux, you will need to bind a serial device before using
this software - eg. rfcomm bind /dev/rfcomm0 PP:QQ:RR:XX:YY:ZZ - and then
specify that device (eg. /dev/rfcomm0) in the port parameter of the T616
constructor function.

Copyright (c) 2003 Nelson Minar <nelson@monkey.org>
http://www.nelson.monkey.org/~nelson/weblog/tech/phone/
Copyright (c) 2005 Paul Boddie <paul@boddie.org.uk>
http://www.boddie.org.uk/paul

This library is free software; you can redistribute it and/or
modify it under the terms of the GNU Lesser General Public
License as published by the Free Software Foundation; either
version 2.1 of the License, or (at your option) any later version.

This library is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
Lesser General Public License for more details.

You should have received a copy of the GNU Lesser General Public
License along with this library; if not, write to the Free Software
Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA
"""

__version__ = "0.1"

try:
    import serial # Requires pySerial http://pyserial.sourceforge.net/
except ImportError:
    serial = None # Requires Bluetooth socket support in Python
import socket, select
import time, re, sys

contactParseRE = re.compile(r"""
  ^\+CPBR:\s
  (?P<pos>\d+),
  "(?P<num>[\dp*#+]+)",
  (?P<zone>\d+),
  "(?P<name>[^/]+)(/(?P<type>\S))?"$""", re.VERBOSE)

def contactParse(s):

    """
    Parse a contact from the phone's format. For example:

    '+CPBR: 4,"5551212",129,"Test/H"'

    Return a tuple of strings describing the contact in the following format:

    (position, number, zone, name, type)
    """

    m = contactParseRE.match(s)
    if not m:
        raise CommandException("Could not parse contact string %s" % repr(s))
    d = m.groupdict()
    return d["pos"], d["num"], d["zone"], d["name"], d["type"]

def contactUnparse(t):

    """
    Return a string like the phone's format. For example:

    4,"5551212",129,"Test/H"
    """

    # Check the type.
    if t[-1] is not None:
        return '%s,"%s",%s,"%s/%s"' % t
    else:
        return '%s,"%s",%s,"%s"' % t[:-1]

class CommandException(Exception):

    "An exception signalling failure in the execution of a command."

    pass
        
class InitException(Exception):

    "An exception signalling failure in the initialisation of a connection."

    pass

class SocketWrapper:

    """
    A wrapper around a socket providing a pySerial-like communications
    interface.
    """

    def __init__(self, socket, timeout):

        """
        Initialise the wrapper with the given 'socket' and a 'timeout' in
        milliseconds.
        """

        self.socket = socket
        self.timeout = timeout
        self.socket.setblocking(1)
        self.poller = select.poll()
        self.poller.register(self.socket, select.POLLIN | select.POLLHUP | select.POLLNVAL | select.POLLERR)

    def write(self, s):

        "Write the string 's' to the socket."

        return self.socket.send(s)

    def read(self, size):

        """
        Read and return a string with a length equal to or less than the given
        'size'. Where no data is available for reading, return an empty string.
        """

        fds = self.poller.poll(self.timeout)
        for fd, status in fds:
            if fd == self.socket.fileno() and status & select.POLLIN:
                s = self.socket.recv(size)
                return s
        return ""

    def close(self):

        "Close the socket."

        self.socket.close()

    # Faked support for the clearing operation.

    def inWaiting(self):
        return 0

class T616:

    """
    A class that encapsulates communications with a Sony Ericsson T610/T616 or
    similar mobile telephone. Works via serial communications, sending AT
    commands to the phone and retrieving results.

    Methods starting with _ are low level communication methods; other methods
    implement higher-level functions.

    Test environment:
      T616 firmware R1A054
      Belkin Bluetooth serial adapter
      Python 2.3.2 on Windows with win32all and pyserial 2.0

    Paul's test environment:
      T610 firmware R6C005
      Linksys Bluetooth USB adapter (USBBT100)
      Python 2.4.1 on Kubuntu 5.04 with pyserial 2.1 (2.1-1ubuntu1) and also
      with Bluetooth sockets

    More info:
    http://www.nelson.monkey.org/~nelson/weblog/tech/phone/
    http://www.ericsson.hu/mobilinternet/products/sh888/888_r1d.pdf
    http://www.boddie.org.uk/python/t616hack.html
    """

    # Message status constants.

    READ, STORED = 1, 2

    # Format constants.

    PDU, TEXT = 0, 1

    # Exceptions (so that users of T616 objects do not have to access the
    # module).

    CommandException = CommandException
    InitException = InitException

    def __init__(self, port=None, baudrate=115200, bdaddr=None, channel=1,
        timeout=1.0, debug=0, clear=0):

        """
        Create a connection to the phone, optionally clear the channel and test
        the connection. The connection can be initialised in the following ways:

          * By using a named serial 'port' or device (for example, "COM1" or
            "/dev/rfcomm0") and by optionally specifying a 'baudrate' (for
            example, 57600).
          * By using a Bluetooth address 'bdaddr' (for example,
            "01:23:45:67:89:AB") and by optionally specifying a 'channel' (the
            default being 1, but this may vary according to the model of the
            telephone being used - see the documentation and output from tools
            such as sdptool).

        Additional information can be specified to configure the connection:

          * The 'timeout' (in seconds, set to 1s by default) indicates how long
            a read operation will wait for more input before returning.
          * The 'debug' parameter, if set to a true value, will print debugging
            information about the commands sent to the device to standard output
            or the console.
          * The 'clear' parameter, if set to a true value, will perform an extra
            read operation after connecting to empty the input buffer of
            possible "noise".
        """

        self.debug = debug
        
        # Open the socket, port or device.
        # Check for a Bluetooth address.

        if bdaddr is not None:
            self.socket = socket.socket(socket.AF_BLUETOOTH, socket.SOCK_STREAM, socket.BTPROTO_RFCOMM)
            try:
                self.socket.connect((bdaddr, channel))
                self.ser = SocketWrapper(self.socket, timeout * 1000)
            except:
                self.socket.close()
                raise

        # Check for pySerial

        elif serial is not None and port is not None:
            self.socket = None
            self.ser = serial.Serial(port=port, baudrate=baudrate, timeout=timeout)

        # Otherwise, signal an error condition.

        else:
            raise InitException, "Without pySerial installed, a Bluetooth address must be given."

        # Turn off command echo.

        self._expect('ATE=0', 'ATE=0\r\r\nOK\r\n')

        # Clear the buffers, if requested.

        if clear:
            time.sleep(0.1)
            self._readWaiting()

        # And test the connection.

        self._expect('AT', '\r\nOK\r\n')

    def _debug(self, s):
        if self.debug: sys.stderr.write(":: %s\n" % s)
        
    def _sendCmd(self, cmd):

        """
        Send the command specified by 'cmd' to the phone. An example of such a
        command is "AT".
        """

        self._debug("Sending %s" % cmd)
        self.ser.write(cmd)
        self.ser.write("\r\n")

    def _readWaiting(self):

        "Read whatever is waiting in the local serial buffer. No timeout."

        c = self.ser.inWaiting()
        return self.ser.read(c)

    def _readAll(self):

        "Read all input available. This relies on the configured timeout."

        buf = []
        while 1:
            r = self.ser.read(512)
            if r:
                buf.append(r)
            else:
                return "".join(buf)

    def _expect(self, cmd, expected):

        """
        Execute the given command 'cmd', verifying the response against
        'expected'. This relies on the configured timeout.
        """

        self._sendCmd(cmd)
        result = self._readAll()
        if not result == expected:
            raise CommandException("Expected %s but got %s" % (repr(expected), repr(result)))

    def getTime(self):

        "Ask the phone what time it thinks it is."

        self._sendCmd("AT+CCLK?")
        r = self._readAll()
        return re.search(r'CCLK: "(.+)"', r).group(1)

    def getVersion(self):

        "Ask what version of firmware the phone has."

        self._sendCmd("AT+CGMR")
        return self._readAll()
    
    def selectMemory(self, type="ME"):

        """
        Select the phone's memory 'type', which can generally be either "ME" or
        "SM".
        """

        self._expect('AT+CPBS="%s"' % type, '\r\nOK\r\n')

    selectPhoneBookStorage = selectMemory

    def getMessageStorageTypes(self, cache=1):

        """
        Find the supported message storage identifiers, returning a tuple
        containing the string identifiers.

        If the optional 'cache' parameter is set to a false value (instead of
        the default true value), override and repopulate the cached values from
        the last time this information was requested.
        """

        # Use the cache if available.
        if cache and hasattr(self, "storage_types"):
            return self.storage_types

        self._sendCmd("AT+CPMS=?")
        cpmsInfo = self._readAll()
        m = re.search(r"\+CPMS: \((.+)\),\((.+)\),\((.+)\)", cpmsInfo)
        if not m:
            raise CommandException("Couldn't parse CPMS info %s" % repr(cpmsInfo))
        results = []
        for group in m.groups():
            result = []
            for identifier in group.split(","):
                result.append(identifier.strip('"'))
            results.append(result)

        # Cache the result.
        self.storage_types = tuple(results)
        return self.storage_types

    def getMessageStorage(self):

        """
        Get the current message storage settings, returning a tuple containing a
        number of 3-tuple elements, each element having the following format:

        storage_identifier, used_spaces_integer, total_spaces_integer
        """

        self._sendCmd("AT+CPMS?")
        cpmsInfo = self._readAll()
        m = re.search(r'\+CPMS: "([A-Z]+)",(\d+),(\d+),"([A-Z]+)",(\d+),(\d+),"([A-Z]+)",(\d+),(\d+)', cpmsInfo)
        if not m:
            raise CommandException("Couldn't parse CPMS info %s" % repr(cpmsInfo))
        g = m.groups()
        results = []
        for i in range(0, len(g), 3):
            result = g[i], int(g[i+1]), int(g[i+2])
            results.append(result)
        return tuple(results)

    def selectMessageStorage(self, type="ME"):

        """
        Select the preferred message storage 'type', which can typically either
        be "ME" or "SM", returning a tuple containing a number of 2-tuple
        elements, each element having the following format:

        used_spaces_integer, total_spaces_integer

        The elements show the storage status for the storage types in order of
        descending preference.
        """

        self._sendCmd('AT+CPMS="%s"' % type)
        cpmsInfo = self._readAll()
        m = re.search(r"\+CPMS: (\d+),(\d+),(\d+),(\d+),(\d+),(\d+)", cpmsInfo)
        if not m:
            raise CommandException("Couldn't parse CPMS info %s" % repr(cpmsInfo))
        g = map(int, m.groups())
        results = []
        for i in range(0, len(g), 2):
            result = g[i], g[i+1]
            results.append(result)
        return tuple(results)

    def readContacts(self):

        """
        Read all the contacts from the phone's selected memory, returning a list
        of tuples, one for each contact found.
        """

        # Ask the phone how many contacts it has.
        # Result is like this: +CPBR: (1-510),80,180

        self._sendCmd("AT+CPBR=?")
        cpbrInfo = self._readAll()
        min, max = self._parseRange("CPBR", cpbrInfo, "-")

        # Ask the phone to dump all the contacts.
        # Result is a list of lines like this: +CPBR: 2,"16506234316",129,"Nelson/W"
        # First and last three lines are not really contacts, so discard them.

        self._sendCmd("AT+CPBR=%s,%s" % (min, max))
        contacts = self._readAll().split('\r\n')[1:-3]

        # Convert the strings to tuples.

        r = []
        for c in contacts:
            try:
                r.append(contactParse(c))
            except Exception, e:
                # NOTE: This should be refined to catch specific exceptions.
                # Continue past parse errors.
                if self.debug:
                    sys.stderr.write("%s\n" % e)
                
        return r

    def writeContact(self, c):

        "Write the contact tuple 'c' to the phone."

        self._expect("AT+CPBW=%s" % contactUnparse(c), "\r\nOK\r\n")

    def getMessageFormats(self, cache=1):

        """
        Return a list of available message formats, typically 0 being PDU
        and 1 being text.

        If the optional 'cache' parameter is set to a false value (instead of
        the default true value), override and repopulate the cached values from
        the last time this information was requested.
        """

        # Use the cache if available.
        if cache and hasattr(self, "message_formats"):
            return self.message_formats
        self._sendCmd("AT+CMGF=?")
        cmgfInfo = self._readAll()

        # Cache the result.
        self.message_formats = self._parseRange("CMGF", cmgfInfo, ",")
        return self.message_formats

    def getMessageFormat(self):

        "Return the current message format - see getMessageFormats."

        self._sendCmd("AT+CMGF?")
        cmgfInfo = self._readAll()
        return self._parseInt("CMGF", cmgfInfo)

    def setMessageFormat(self, format):

        "Set the current message 'format' - see getMessageFormats."

        self._expect('AT+CMGF=%s' % format, '\r\nOK\r\n')

    def getCharacterSets(self, cache=1):

        """
        Return the available character sets as a list of string identifiers.

        If the optional 'cache' parameter is set to a false value (instead of
        the default true value), override and repopulate the cached values from
        the last time this information was requested.
        """

        # Use the cache if available.
        if cache and hasattr(self, "character_sets"):
            return self.character_sets

        self._sendCmd("AT+CSCS=?")
        cscsInfo = self._readAll()

        # Cache the result.
        self.character_sets = self._parseList("CSCS", cscsInfo)
        return self.character_sets

    def getCharacterSet(self):

        "Return the current character set."

        self._sendCmd("AT+CSCS?")
        cscsInfo = self._readAll()
        return self._parseGeneral("CSCS", cscsInfo)

    def setCharacterSet(self, charset):

        """
        Set the current character set using the 'charset' string identifier,
        possibly obtained from getCharacterSets.
        """

        self._expect('AT+CSCS="%s"' % charset, '\r\nOK\r\n')

    def getMessageStatusCodes(self):

        """
        Return the available message status codes for the current message
        format as a list.
        """

        self._sendCmd("AT+CMGL=?")
        cmglInfo = self._readAll()
        if self.getMessageFormat() == 0:
            min, max = self._parseRange("CMGL", cmglInfo, "-")
            return range(min, max + 1)
        else:
            return self._parseList("CMGL", cmglInfo)

    def getApplicationFunctions(self):

        "Returns a list of supported functions."

        self._sendCmd("AT*EAPP=?")
        functions = []
        for line in self._readAll().split("\r\n"):
            if line.startswith("*EAPP:"):
                functions.append(self._parseFunction(line))
        return functions

    def readMessagesRaw(self, code=None):

        """
        Read messages in the phone's memory, selecting all messages by default.

        An optional 'code' overrides the retrieved messages and should be
        defined according to the following rules:

          * With the PDU message format selected, 'code' should be an integer
            produced by combining this class's special attributes STORED and
            READ, defining whether received and unread messages are to be
            respectively ignored.
          * With the text message format selected, 'code' should be a suitable
            string identifier such as "ALL".

        For both message formats, sets of valid codes can be obtained using the
        getMessageStatusCodes method.

        The raw response string containing the message headers and bodies is
        returned from this method.
        """

        # Get an appropriate request code.
        if code is None:
            code = self.getMessageStatusCodes()[-1]
        elif code not in self.getMessageStatusCodes():
            raise CommandException("Code %s was apparently not supported" % code)

        # Send the code and interpret the response.
        if type(code) == type(0):
            self._sendCmd("AT+CMGL=%s" % code)
        else:
            self._sendCmd('AT+CMGL="%s"' % code)
        response = self._readAll()
        return response

    def readMessages(self, code=None):

        """
        Read messages in the phone's memory, selecting all messages by default.

        An optional 'code' overrides the retrieved messages and should be
        defined according to the following rules:

          * With the PDU message format selected, 'code' should be an integer
            produced by combining this class's special attributes STORED and
            READ, defining whether received and unread messages are to be
            respectively ignored.
          * With the text message format selected, 'code' should be a suitable
            string identifier such as "ALL".

        For both message formats, sets of valid codes can be obtained using the
        getMessageStatusCodes method.

        Messages are returned as tuples each containing the message details and
        the raw response string."""

        messageLines = self.readMessagesRaw(code).split("\r\n")[1:-3]
        messages = []
        i = 0
        while i < len(messageLines):
            messageDetails = self._parseHeader("CMGL", messageLines[i])
            messageBodyLines = []
            i += 1
            while i < len(messageLines) and not messageLines[i].startswith("+CMGL"):
                messageBodyLines.append(messageLines[i])
                i += 1
            messages.append((messageDetails, "".join(messageBodyLines)))
        return messages

    def readMessageRaw(self, index):

        """
        Read the message at position 'index' in the currently selected storage
        and return it as a raw response string.
        """

        self._sendCmd("AT+CMGR=%s" % index)
        response = self._readAll()
        if response.startswith("\r\n+CMS ERROR"):
            raise CommandException("Could not read message %d info %s" % (index, repr(response)))
        return response

    def readMessage(self, index):

        """
        Read the message at position 'index' in the currently selected storage
        and return it as a tuple containing the message details.
        """

        messageLines = self.readMessageRaw(index).split("\r\n")[1:-3]
        messageDetails = self._parseHeader("CMGR", messageLines[0])
        i = 1
        messageBodyLines = []
        while i < len(messageLines) and not messageLines[i].startswith("+CMGR"):
            messageBodyLines.append(messageLines[i])
            i += 1
        return (messageDetails, "".join(messageBodyLines))

    def deleteMessage(self, index):

        """
        Delete the message at position 'index' in the currently selected
        storage.
        """

        self._expect("AT+CMGD=%s" % index, "\r\nOK\r\n")

    # Internal parsing methods.

    def _parseGeneral(self, command, response):
        m = re.search(r'\+%s: ([^\r]+)' % command, response)
        if not m:
            raise CommandException("Couldn't parse %s info %s" % (command, repr(response)))
        return m.groups()[0].strip('"')

    def _parseInt(self, command, response):
        m = re.search(r'\+%s: (\d+)' % command, response)
        if not m:
            raise CommandException("Couldn't parse %s info %s" % (command, repr(response)))
        return int(m.groups()[0])

    def _parseList(self, command, response):
        m = re.search(r'\+%s: \(([^\)]+)\)' % command, response)
        if not m:
            raise CommandException("Couldn't parse %s info %s" % (command, repr(response)))
        identifiers = m.groups()[0].split(",")
        return [identifier.strip('"') for identifier in identifiers]

    def _parseHeader(self, command, response):
        m = re.search(r'\+%s: ([^\r]+)' % command, response)
        if not m:
            raise CommandException("Couldn't parse %s info %s" % (command, repr(response)))
        identifiers = m.groups()[0].split(",")
        return [identifier.strip('"') for identifier in identifiers]

    def _parseRange(self, command, response, delimiter):
        m = re.search(r'\+%s: \((\d+)%s(\d+)\)' % (command, delimiter), response)
        if not m:
            raise CommandException("Couldn't parse %s info %s" % (command, repr(response)))
        return map(int, m.groups())

    def _parseFunction(self, response):
        m = re.search(r'(\d+), \((\d+(-\d+)?(,\d+(-\d+)?)*)\)', response)
        if not m:
            raise CommandException("Couldn't parse function info %s" % repr(response))
        function = int(m.groups()[0])
        subfunctions = []
        for element in m.groups()[1].split(","):
            subelements = element.split("-")
            if len(subelements) < 2:
                subfunctions.append(int(subelements[0]))
            else:
                subfunctions += range(int(subelements[0]), int(subelements[1]) + 1)
        return function, subfunctions

    def close(self):

        "Close the phone connection politely."

        try:
            self._sendCmd('ATE=1')
        finally:    
            self.ser.close()

# Tests.

def test():
    c1 = '+CPBR: 4,"5551212",129,"Test/H"'
    contact = contactParse(c1)
    assert ('4', '5551212', '129', 'Test', 'H') == contact
    assert c1[7:] == contactUnparse(contact)

    c2 = '+CPBR: 6,"9p9*#9+9",129,"Tdpt_/H"'
    contact = contactParse(c2)
    assert ('6', '9p9*#9+9', '129', 'Tdpt_', 'H') == contact
    assert c2[7:] == contactUnparse(contact)

if __name__=='__main__':
    print "Running tests"
    test()

# vim: tabstop=4 expandtab shiftwidth=4
