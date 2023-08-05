#!/usr/bin/env python

"""
Download messages from storage on the telephone, storing them in a file.

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

from T616 import T616, CommandException
import codecs
import sys
import cmdsyntax

if __name__ == "__main__":
    syntax = cmdsyntax.Syntax("""
        <datafile> <memory>
        ( ( --port=PORT [--baudrate=BAUDRATE] ) | ( --bdaddr=BDADDR [--channel=CHANNEL] ) )
        [--raw] [--debug]
        [--encoding=ENCODING]
        """)
    matches = syntax.get_args(sys.argv[1:])
    try:
        args = matches[0]
    except (IndexError, ValueError), exc:
        print "Syntax:"
        print syntax.syntax
        print "Please specify:"
        print "  A file, <datafile>, into which messages will be written."
        print "  The memory from which messages will be read; for example: ME, SM."
        print
        print "Please also specify a port (and baudrate); for example:"
        print "  --port=/dev/rfcomm0 --baudrate=57600"
        print "  --port=COM1"
        print "Or instead specify a Bluetooth address (and channel); for example:"
        print "  --bdaddr=01:23:45:67:89:AB --channel=1"
        print
        print "If the --raw argument is also specified, the messages will be"
        print "written out as they were received from the telephone."
        print
        print "If the --encoding argument is specified, the given encoding will be"
        print "used in the output file, <datafile>."
        sys.exit(1)

    datafile = args["datafile"]
    memory = args["memory"]
    encoding = args.get("encoding", "utf-8")

    if args.has_key("channel"):
        channel = int(args["channel"])
    else:
        channel = None
    if args.has_key("baudrate"):
        baudrate = int(args["baudrate"])
    else:
        baudrate = None

    p = T616(port=args.get("port"), baudrate=baudrate, bdaddr=args.get("bdaddr"), channel=channel, debug=args.has_key("debug"))

    if args.has_key("raw"):
        fp = open(datafile, "wb")
    else:
        fp = codecs.open(datafile, "wb", encoding=encoding)

    try:
        p.selectMessageStorage(memory)

        # Set the message format.

        p.setCharacterSet("UTF-8")
        p.setMessageFormat(p.TEXT)

        try:
            if args.has_key("raw"):
                fp.write(p.readMessagesRaw())
            else:
                messages = p.readMessages()
                print "Read %d messages from %s" % (len(messages), memory)
        
                for header, message in messages:
                    index, status = header[0:2]
                    if len(header) >= 6:
                        number, name, date, time = header[2:6]
                        fp.write("Date: %s\n" % date)
                        fp.write("Time: %s\n" % time)
                        fp.write("From: %s <%s>\n" % (name, number))
                    fp.write("Message-Id: <%s-%s>\n" % (memory, index))
                    fp.write("Status: %s\n" % status)
                    fp.write("\n" + message + "\n\n")

            print "Wrote to file %s" % datafile
        except CommandException, exc:
            print "Reading failed with exception:", str(exc)

    finally:
        fp.close()
        p.close()

# vim: tabstop=4 expandtab shiftwidth=4
