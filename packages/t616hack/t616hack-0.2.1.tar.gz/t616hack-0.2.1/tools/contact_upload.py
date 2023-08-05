#!/usr/bin/env python

"""
Upload phone contacts to memory from disk.
Note that this will overwrite records in your contact list!

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

    fp = file(datafile, "rb")
    contacts = eval(fp.read())
    fp.close()
    print "Preparing to upload %d contacts" % len(contacts)

    try:
        p.selectPhoneBookStorage(memory)

        # Set the message format.

        p.setCharacterSet("UTF-8")

        for contact in contacts:
            print "Writing", contact
            p.writeContact(contact)

    finally:
        p.close()

# vim: tabstop=4 expandtab shiftwidth=4
