#!/usr/bin/env python

"""
Download phone contacts from memory, store them to disk.

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

from T616 import T616
import sys

if __name__ == "__main__":
    try:
        debug = ("--debug" in sys.argv)
        datafile = sys.argv[1]
        memory = sys.argv[2]
        if "--port" in sys.argv:
            __port = sys.argv.index("--port")
            port = sys.argv[__port + 1]

            if "--baudrate" in sys.argv:
                __baudrate = sys.argv.index("--baudrate")
                baudrate = int(sys.argv[__baudrate + 1])
            else:
                baudrate = None

            bdaddr = None
            channel = None

        else: # "--bdaddr" in sys.argv:
            __bdaddr = sys.argv.index("--bdaddr")
            bdaddr = sys.argv[__bdaddr + 1]
            if "--channel" in sys.argv:
                __channel = sys.argv.index("--channel")
                channel = int(sys.argv[__channel + 1])
            else:
                channel = None

            port = None
            baudrate = None

    except (IndexError, ValueError), exc:
        print "Please specify a file into which contacts will be written."
        print "For example: contacts.txt"
        print "Please also specify the memory from which contacts will be read."
        print "For example: SM, ME."
        print
        print "Please also specify a port (and baudrate); for example:"
        print "  --port /dev/rfcomm0 --baudrate 57600"
        print "  --port COM1"
        print "Or instead specify a Bluetooth address (and channel); for example:"
        print "  --bdaddr 01:23:45:67:89:AB --channel 1"
        sys.exit(1)

    if port is not None:
        if baudrate is not None:
            p = T616(port=port, baudrate=baudrate, debug=debug)
        else:
            p = T616(port=port, debug=debug)
    else:
        if channel is not None:
            p = T616(bdaddr=bdaddr, channel=channel, debug=debug)
        else:
            p = T616(bdaddr=bdaddr, debug=debug)

    fp = file(datafile, "wb")

    try:
        p.selectPhoneBookStorage(memory)

        # Set the message format.

        p.setCharacterSet("UTF-8")

        contacts = p.readContacts()
        print "Read %d contacts" % len(contacts)
        
        fp.write(repr(contacts))
        print "Wrote to file %s" % datafile

    finally:
        fp.close()
        p.close()

# vim: tabstop=4 expandtab shiftwidth=4
