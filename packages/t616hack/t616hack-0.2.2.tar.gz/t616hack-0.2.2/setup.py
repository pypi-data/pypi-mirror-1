#! /usr/bin/env python

from distutils.core import setup

import T616

setup(
    name         = "t616hack",
    description  = "Contact and phonebook access for the Sony Ericsson T610/T616",
    author       = "Paul Boddie", # for this package - see docs/COPYING.txt
    author_email = "paul@boddie.org.uk",
    url          = "http://www.boddie.org.uk/python/t616hack.html",
    version      = T616.__version__,
    py_modules   = ["T616"],
    scripts      = ["tools/contact_download.py", "tools/contact_upload.py",
                    "tools/message_download.py", "tools/Nokia_converter.py",
                    "tools/write_message.py"]
    )
