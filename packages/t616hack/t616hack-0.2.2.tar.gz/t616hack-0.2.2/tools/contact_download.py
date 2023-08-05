#!/usr/bin/env python

"""
Download phone contacts from memory, store them to disk.

Copyright (c) 2003 Nelson Minar <nelson@monkey.org>
http://www.nelson.monkey.org/~nelson/weblog/tech/phone/
Copyright (c) 2005, 2006 Paul Boddie <paul@boddie.org.uk>
http://www.boddie.org.uk/paul

This program is free software; you can redistribute it and/or modify it under
the terms of the GNU Lesser General Public License as published by the Free
Software Foundation; either version 3 of the License, or (at your option) any
later version.

This program is distributed in the hope that it will be useful, but WITHOUT
ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
FOR A PARTICULAR PURPOSE.  See the GNU Lesser General Public License for more
details.

You should have received a copy of the GNU Lesser General Public License along
with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

from T616 import T616
import sys
import cmdsyntax

if __name__ == "__main__":
    syntax = cmdsyntax.Syntax("""
        <datafile> <memory>
        ( ( --port=PORT [--baudrate=BAUDRATE] ) | ( --bdaddr=BDADDR [--channel=CHANNEL] ) )
        [--debug]
        """)
    matches = syntax.get_args(sys.argv[1:])
    try:
        args = matches[0]
    except (IndexError, ValueError), exc:
        print "Syntax:"
        print syntax.syntax
        print "Please specify:"
        print "  A file, <datafile>, into which contacts will be written."
        print "  The memory from which messages will be read; for example: ME, SM."
        print
        print "Please also specify a port (and baudrate); for example:"
        print "  --port=/dev/rfcomm0 --baudrate=57600"
        print "  --port=COM1"
        print "Or instead specify a Bluetooth address (and channel); for example:"
        print "  --bdaddr=01:23:45:67:89:AB --channel=1"
        sys.exit(1)

    datafile = args["datafile"]
    memory = args["memory"]

    if args.has_key("channel"):
        channel = int(args["channel"])
    else:
        channel = None
    if args.has_key("baudrate"):
        baudrate = int(args["baudrate"])
    else:
        baudrate = None
    p = T616(port=args.get("port"), baudrate=baudrate, bdaddr=args.get("bdaddr"), channel=channel, debug=args.has_key("debug"))

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
