#!/usr/bin/env python

"""
A demonstration of the T616 module.

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

from T616 import *
import sys

if __name__ == "__main__":

    try:
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
        print "Please specify a port (and baudrate); for example:"
        print "  --port /dev/rfcomm0 --baudrate 57600"
        print "  --port COM1"
        print "Or instead specify a Bluetooth address (and channel); for example:"
        print "  --bdaddr 01:23:45:67:89:AB --channel 1"
        sys.exit(1)

    if port is not None:
        if baudrate is not None:
            p = T616(port=port, baudrate=baudrate, debug=1)
        else:
            p = T616(port=port, debug=1)
    else:
        if channel is not None:
            p = T616(bdaddr=bdaddr, channel=channel, debug=1)
        else:
            p = T616(bdaddr=bdaddr, debug=1)

    try:
        print "Reading version"
        print p.getVersion()
        print "Reading time"
        print p.getTime()
        p.selectMemory()
        print "Reading memory contacts"
        print p.readContacts()
    finally:
        p.close()

# vim: tabstop=4 expandtab shiftwidth=4
