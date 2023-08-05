#!/usr/bin/env python

"""
Write a message to storage on the telephone.

Copyright (c) 2006 Paul Boddie <paul@boddie.org.uk>
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
        [--debug]
        [--encoding=ENCODING]
        """)
    matches = syntax.get_args(sys.argv[1:])
    try:
        args = matches[0]
    except (IndexError, ValueError), exc:
        print "Syntax:"
        print syntax.syntax
        print "Please specify:"
        print "  A file, <datafile>, from which messages will be read. This may be"
        print "  given as - to indicate that standard input shall be read instead."
        print "  The memory from which messages will be read; for example: ME, SM."
        print
        print "Please also specify a port (and baudrate); for example:"
        print "  --port=/dev/rfcomm0 --baudrate=57600"
        print "  --port=COM1"
        print "Or instead specify a Bluetooth address (and channel); for example:"
        print "  --bdaddr=01:23:45:67:89:AB --channel=1"
        print
        print "If the --encoding argument is specified, the given encoding will be"
        print "used when reading the input file, <datafile>."
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

    if datafile != "-":
        fp = codecs.open(datafile, "rb", encoding=encoding)
    else:
        fp = codecs.getreader(sys.stdin.encoding)(sys.stdin)

    try:
        p.selectMessageStorage(memory, memory)

        try:
            if datafile == "-":
                print "Please type your message now. End with Ctrl-D."
            message_text = fp.read()
            p.writeMessage(message_text)
            if datafile != "-":
                print "Read from file %s" % datafile
            else:
                print "Read from standard input."
        except CommandException, exc:
            print "Reading failed with exception:", str(exc)

    finally:
        if datafile != "-":
            fp.close()
        p.close()

# vim: tabstop=4 expandtab shiftwidth=4
