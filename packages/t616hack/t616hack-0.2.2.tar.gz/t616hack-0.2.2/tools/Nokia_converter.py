#!/usr/bin/env python

"""
Convert input in Nokia CSV format to a contacts data structure.
Data was downloaded via Nokia 3360 PC Suite
http://www.nokiausa.com/phones/software/3360
Conversion is best-effort. ASCII only, etc.

Copyright (c) 2003 Nelson Minar <nelson@monkey.org>
http://www.nelson.monkey.org/~nelson/weblog/tech/phone/
"""

import sys

nokiaFile='PhoneBook.csv'
outFile='converted.txt'

def convertType(nokiaCode):
    "Map Nokia contact type codes to Ericsson type codes"
    types = {
        u'210': 'M',
        u'209': 'H',
        u'213': 'W',
        u'219': 'G',
        u'205': 'E',
    }
    default = 'H'
    try:
        r = types[nokiaCode]
    except Exception:
        sys.stderr.write("Unknown Nokia type code %s\n" % nokiaCode)
        r = default
    if r == 'G':         # Nokia has an unknown type; Ericsson doesn't
        r = default
    return r

def convertNumber(nokiaNumber):
    r = nokiaNumber.encode('ascii')
    return r.replace('w', 'p')        # Ericsson doesn't seem to have wait

def test():
    sys.stderr.write("Running tests\n")
    assert 'W' == convertType(u'213')
    assert 'H' == convertType(u'219')
    assert 'H' == convertType(u'invalid')
    assert '5551212' == convertNumber(u'5551212')
    assert '5551212p*p' == convertNumber(u'5551212p*p')

test()

import codecs
infile = codecs.open(nokiaFile, "r", "utf-16")
converted = []
position = 1

for contact in infile.read().split('\r\n'):
    data = contact.split('\t')

    # No idea what the first 3 fields mean, but all my contacts had them
    if not ([u'200', u'PIT_CONTACT', u'202']) == data[:3]:
        sys.stderr.write("Can't parse %s\n" % contact)
        continue

    # Get the main name, strip it to ASCII
    name = data[3].encode('ascii', 'replace')

    # Now for each appropriate contact, append it to converted
    for i in range(4, len(data), 2):
        type = convertType(data[i])
        number = convertNumber(data[i+1])
        if type == 'E':
            sys.stderr.write("Skipping email record %s %s\n" % (name, number))
        else:
            converted.append((str(position),
                              number,
                              '129',
                              name,
                              type))
            position += 1

fp = file(outFile, "w")
fp.write(repr(converted))
fp.close()
print "Saved to %s" % outFile


#for l in infile:
#    print repr(l.decode('UTF-16'))
    
# vim: tabstop=4 expandtab shiftwidth=4
