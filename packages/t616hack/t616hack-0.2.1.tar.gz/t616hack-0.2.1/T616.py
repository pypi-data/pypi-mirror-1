#!/usr/bin/env python

"""
Talk to a T616/T610 via a serial or Bluetooth socket connection and make it do
various things.

Copyright (c) 2003 Nelson Minar <nelson@monkey.org>
http://www.nelson.monkey.org/~nelson/weblog/tech/phone/
Copyright (c) 2005, 2006 Paul Boddie <paul@boddie.org.uk>
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

__version__ = "0.2.1"

try:
    import serial # Requires pySerial http://pyserial.sourceforge.net/
except ImportError:
    serial = None # Requires Bluetooth socket support in Python
import socket, select
import time, re, sys

# Contact parsing functionality.

contactParseRE = re.compile(r"""
  ^\+CPBR:\s
  (?P<pos>\d+),
  "(?P<num>[\dA-Fp*#+]+)",
  (?P<zone>\d+),
  "(?P<name>[^"]+)"$""", re.VERBOSE)

def contactParse(s, charset):

    """
    Parse a contact from the phone's format. For example:

    '+CPBR: 4,"5551212",129,"Test/H"'

    Return a tuple of strings describing the contact in the following format:

    (position, number, zone, name, type)

    Note that type may be None if no type details were found.
    """

    m = contactParseRE.match(s)
    if not m:
        raise CommandException("Could not parse contact string %s" % repr(s))
    d = m.groupdict()
    name_and_type = from_phone(d["name"], charset)
    if len(name_and_type) > 1 and name_and_type[-2] == "/":
        name, type = name_and_type[:-2], name_and_type[-1]
    else:
        name, type = name_and_type, None
    return d["pos"], from_phone(d["num"], charset), d["zone"], name, type

def contactUnparse(t, charset):

    """
    Return a string like the phone's format. For example:

    4,"5551212",129,"Test/H"
    """

    position, number, zone, name, type = t

    # Check the type.
    if type is not None:
        return '%s,"%s",%s,"%s"' % (position, to_phone(number, charset), zone, to_phone(name + "/" + type, charset))
    else:
        return '%s,"%s",%s,"%s"' % (position, to_phone(number, charset), zone, to_phone(name, charset))

# Exception classes, available on the T616 class itself.

class CommandException(Exception):

    "An exception signalling failure in the execution of a command."

    pass
        
class InitException(Exception):

    "An exception signalling failure in the initialisation of a connection."

    pass

# Communications helper classes and functions.

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

    def getTimeout(self):
        return self.timeout

    def setTimeout(self, timeout):
        self.timeout = timeout

    # Faked support for the clearing operation.

    def inWaiting(self):
        return 0

# Character set helper functions.
# NOTE: Should possibly consider genuine Unicode codecs.
# NOTE: Should also fix GSM alphabet support.

def to_phone(s, charset):

    "Encode the given Unicode object 's' using the given 'charset'."

    if charset == "UCS2":
        return to_ucs2(s)
    elif charset is None or charset in ("GSM", "IRA"):
        return s.encode("ascii")
    else:
        return s.encode(charset)

def from_phone(s, charset):

    "Return the given string 's', encoded with 'charset', as a Unicode object."

    if charset == "UCS2":
        return from_ucs2(s)
    elif charset is None or charset in ("GSM", "IRA"):
        return unicode(s, "ascii")
    else:
        return unicode(s, charset)

def to_ucs2(s):

    "Encode the given Unicode object 's' as a UCS-2 string."

    l = []
    for c in unicode(s):
        l.append(("%04x" % ord(c)).upper())
    return "".join(l)

def from_ucs2(s):

    "Return the given UCS-2 string 's' as a Unicode object."

    l = []
    for i in range(0, len(s), 4):
        c = s[i:i+4]
        l.append(unichr(int(c, 16)))
    return "".join(l)

# The core functionality.

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
    http://www.boddie.org.uk/python/t616hack.html
    http://www.nelson.monkey.org/~nelson/weblog/tech/phone/
    http://www.ericsson.hu/mobilinternet/products/sh888/888_r1d.pdf
    """

    # Message status constants.

    READ, STORED = 1, 2

    # Format constants.

    PDU, TEXT = 0, 1

    # Exceptions (so that users of T616 objects do not have to access the
    # module).

    CommandException = CommandException
    InitException = InitException

    def __init__(self, port=None, baudrate=None, bdaddr=None, channel=None,
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
        if channel is None:
            channel = 1
        if baudrate is None:
            baudrate = 115200
        
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

        # Check for pySerial.

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

        # Finally, set the character set.

        self.charset = None
        self.charset = self.getCharacterSet()

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

    # Public methods.

    def getTime(self):

        "Ask the phone what time it thinks it is."

        self._sendCmd("AT+CCLK?")
        r = self._readAll()
        return from_phone(re.search(r'CCLK: "(.+)"', r).group(1), self.charset)

    def getVersion(self):

        "Ask what version of firmware the phone has."

        self._sendCmd("AT+CGMR")
        return self._readAll()
    
    def selectMemory(self, type="ME"):

        """
        Select the phone's memory 'type', which can generally be either "ME" or
        "SM".
        """

        type = to_phone(type, self.charset)
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
        m = re.search(r'\+CPMS: \((.+)\),\((.+)\),\((.+)\)', cpmsInfo)
        if not m:
            raise CommandException("Couldn't parse CPMS info %s" % repr(cpmsInfo))
        results = []
        for group in m.groups():
            result = []
            for identifier in group.split(","):
                result.append(from_phone(identifier.strip('"'), self.charset))
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
        m = re.search(r'\+CPMS: "([A-Z0-9]+)",(\d+),(\d+),"([A-Z0-9]+)",(\d+),(\d+),"([A-Z0-9]+)",(\d+),(\d+)', cpmsInfo)
        if not m:
            raise CommandException("Couldn't parse CPMS info %s" % repr(cpmsInfo))
        g = m.groups()
        results = []
        for i in range(0, len(g), 3):
            result = from_phone(g[i], self.charset), int(g[i+1]), int(g[i+2])
            results.append(result)
        return tuple(results)

    def selectMessageStorage(self, type="ME", mem2=None, mem3=None):

        """
        Select the preferred message storage 'type', which can typically either
        be "ME" or "SM", along with the optional 'mem2' and 'mem3' values
        (selecting the second and third message storage types), returning a
        tuple containing a number of 2-tuple elements, each element having the
        following format:

        used_spaces_integer, total_spaces_integer

        The elements show the storage status for the storage types in order of
        descending preference.
        """

        cmd = 'AT+CPMS="%s"' % to_phone(type, self.charset)
        if mem2: cmd += ',"%s"' % to_phone(mem2, self.charset)
        if mem3: cmd += ',"%s"' % to_phone(mem3, self.charset)
        self._sendCmd(cmd)
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
                r.append(contactParse(c, self.charset))
            except Exception, e:
                # NOTE: This should be refined to catch specific exceptions.
                # Continue past parse errors.
                if self.debug:
                    sys.stderr.write("%s\n" % e)
                
        return r

    def writeContact(self, c):

        "Write the contact tuple 'c' to the phone."

        self._expect("AT+CPBW=%s" % contactUnparse(c, self.charset), "\r\nOK\r\n")

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
        self.character_sets = [from_phone(s, self.charset) for s in self._parseList("CSCS", cscsInfo)]
        return self.character_sets

    def getCharacterSet(self):

        "Return the current character set."

        self._sendCmd("AT+CSCS?")
        cscsInfo = self._readAll()
        return from_phone(self._parseGeneral("CSCS", cscsInfo), self.charset)

    def setCharacterSet(self, charset):

        """
        Set the current character set using the 'charset' string identifier,
        possibly obtained from getCharacterSets.
        """

        self._expect('AT+CSCS="%s"' % to_phone(charset, self.charset), '\r\nOK\r\n')
        self.charset = charset

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
            return [from_phone(code, self.charset) for code in self._parseList("CMGL", cmglInfo)]

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

        return self._readMessagesRaw(code)

    def _checkMessageStatusCode(self, code):

        # Get an appropriate request code.
        if code is None:
            code = self.getMessageStatusCodes()[-1]
        elif code not in self.getMessageStatusCodes():
            raise CommandException("Code %s was apparently not supported" % code)
        return code

    def _readMessagesRaw(self, code):

        "Read the raw messages using the given 'code'."

        code = self._checkMessageStatusCode(code)

        # Send the code and interpret the response.
        if type(code) == type(0):
            self._sendCmd("AT+CMGL=%s" % code)
        else:
            code = to_phone(code, self.charset)
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

        messageLines = self._readMessagesRaw(code).split("\r\n")[1:-3]
        messages = []
        i = 0
        while i < len(messageLines):
            messageDetails = self._parseHeader("CMGL", messageLines[i])

            # Convert strings in the message details to Unicode.

            messageDetails = [messageDetails[0]] + [from_phone(field, self.charset) for field in messageDetails[1:]]

            # Collect the body lines together and combine the details and body.

            messageBodyLines = []
            i += 1
            while i < len(messageLines) and not messageLines[i].startswith("+CMGL"):
                messageBodyLines.append(messageLines[i])
                i += 1
            messages.append((messageDetails, from_phone("".join(messageBodyLines), self.charset)))

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

        # Convert strings to Unicode for all fields.

        messageDetails = [from_phone(field, self.charset) for field in messageDetails]

        # Collect the body lines together and return the combined details and
        # body.

        i = 1
        messageBodyLines = []
        while i < len(messageLines) and not messageLines[i].startswith("+CMGR"):
            messageBodyLines.append(messageLines[i])
            i += 1
        return (messageDetails, from_phone("".join(messageBodyLines), self.charset))

    def deleteMessage(self, index):

        """
        Delete the message at position 'index' in the currently selected
        storage.
        """

        self._expect("AT+CMGD=%s" % index, "\r\nOK\r\n")

    def writeMessage(self, message, sender="", timeout=5):

        """
        Write the given 'message' (a Unicode object), optionally specifying the
        'sender' (a Unicode object containing an international telephone number
        without any non-numeric characters, such as the leading "+" character).
        The optional 'timeout' (in seconds, default 5 seconds) specifies the
        length of time that should be used to wait for the storage of the
        message.
        """

        # Switch character set and message format.

        format = self.getMessageFormat()
        charset = self.getCharacterSet()
        self.setMessageFormat(self.TEXT)
        self.setCharacterSet("UCS2")

        try:
            self.ser.write('AT+CMGW')
            self.ser.write('="%s"\r' % to_ucs2(sender))
            response = self._readAll()
            if response != '\r\n> \x00':
                raise CommandException("Could not understand response %s" % repr(response))
            self.ser.write(to_ucs2(message) + chr(26))
            self._debug("(Message sent using AT+CMGW...)")

            # Wait longer than usual for the result.

            old_timeout = self.ser.getTimeout()
            self.ser.setTimeout(timeout * 1000)
            response = self._readAll()
            self.ser.setTimeout(old_timeout)
            if response != '\r\nOK\r\n':
                raise CommandException("Could not understand response %s" % repr(response))

        finally:

            # Reset the character set and message format.

            self.setCharacterSet(charset)
            self.setMessageFormat(format)

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
