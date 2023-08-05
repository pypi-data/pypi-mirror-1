Introduction
------------

The t616hack distribution is derived from Nelson Minar's original work in
providing access to the contact list (or phonebook) in the Sony Ericsson T616.
The code has since been updated for the retrieval of text messages, and has
been tested to work over a Bluetooth link using either Bluetooth networking
sockets or a serial port or device (such as COM1 on Windows or /dev/rfcomm0 on
Linux).

Choosing a Communications Mechanism
-----------------------------------

Where available, Bluetooth networking is easier to use. First, discover the
address of your device; then supply that address as the 'bdaddr' in the
various tools and APIs. Discovering addresses can be done by making devices
visible and then using the Linux hcitool program as follows:

hcitool scan

It may be necessary to specify an additional 'channel' parameter to the tools
and APIs. This can be discovered using the Linux sdptool program as follows:

sdptool browse <bdaddr>

If Bluetooth networking is not available, but where a serial port or device
has been set up, the port or device identifier may be supplied as the 'port'
in the various tools and APIs. Sometimes, reliability may be improved by
setting a different transmission rate to the default, supplying a 'baudrate'
(such as 57600) to the various tools and APIs.

Contact, Copyright and Licence Information
------------------------------------------

The current Web page for t616hack at the time of release is:

http://www.boddie.org.uk/python/t616hack.html

Copyright and licence information can be found in the docs directory - see
docs/COPYING.txt and docs/LICENCE.txt for more information.

Dependencies
------------

The t616hack distribution depends on either pySerial or the availability of
Bluetooth sockets in Python. See the following site for pySerial:

http://pyserial.sourceforge.net/

Release Procedures
------------------

Update the T616 __version__ attribute.
Change the version number and package filename/directory in the documentation.
Update the release notes (see above).
Check the release information in the PKG-INFO file.
Tag, export.
Archive, upload.
Update PyPI, PythonInfo Wiki, Vaults of Parnassus entries.

Making Packages
---------------

To make Debian-based packages:

  1. Create new package directories under packages if necessary.
  2. Make a symbolic link in the distribution's root directory to keep the
     Debian tools happy:

     ln -s packages/ubuntu-hoary/python2.4-t616hack/debian/

  3. Run the package builder:

     dpkg-buildpackage -rfakeroot

  4. Locate and tidy up the packages in the parent directory of the
     distribution's root directory.

Edited Original Information
===========================

T616 hacking in Python
----------------------

by Nelson Minar <nelson@monkey.org> 2003-11-16
http://www.nelson.monkey.org/~nelson/weblog/tech/phone/

This code is a demonstration of talking to a Sony Ericsson T616 phone
via AT commands. It's a demonstration only, not production code, but
it may be interesting for the random hacker to get a start on playing
with their phone. I used this code to upload a set of contacts I had
downloaded off of my Nokia phone.

All this stuff is undocumented and unsupported. It's possible this
code could do bad things to your phone. I wrote and ran this on a
WinXP box talking to my T616 over a Bluetooth serial link.

Some useful references to Ericsson AT commands:

http://www.ericsson.hu/mobilinternet/products/sh888/888_r1d.pdf
http://www.ericsson.com/mobilityworld/developerszonedown/downloads/docs/r320/R320s_WP_R1A.pdf
http://www.anotherurl.com/library/at_test.htm
http://www.google.com/search?q=CPBR+ericsson
https://sourceforge.net/projects/fma/
