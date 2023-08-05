#!/usr/bin/env python
"""VObject: module for reading vCard and vCalendar files

Parses iCalendar and vCard files into Python data structures, decoding the relevant encodings. Also serializes vobject data structures to iCalendar, vCard, or (expirementally) hCalendar unicode strings.

Requires python 2.4 or later, dateutil (http://labix.org/python-dateutil) 1.1 or later.

Recent changes: Merge in Apple CalendarServer patches, improve recurring VTODO support

For older changes, see http://vobject.skyhouseconsulting.com/history.html or http://websvn.osafoundation.org/listing.php?repname=vobject&path=/trunk/

"""

# not using setuptools until Chandler's ready for eggs
from ez_setup import use_setuptools
use_setuptools()

from setuptools import setup, find_packages

#from distutils.core import setup

# Metadata
PACKAGE_NAME = "vobject"
PACKAGE_VERSION = "0.4.4"

ALL_EXTS = ['*.py', '*.ics', '*.txt']

packages = ['vobject']

doclines = __doc__.splitlines()

setup(name = "vobject",
      version = PACKAGE_VERSION,
      author = "Jeffrey Harris",
      author_email = "jeffrey@osafoundation.org",
      license = "Apache",
      zip_safe = True,
      url = "http://vobject.skyhouseconsulting.com",

      package_dir = {'':'src'},
      package_data = {'': ALL_EXTS},

      install_requires = ['python-dateutil >= 1.1'], 

      platforms = ["any"],
      packages = ["vobject"],
      description = doclines[0],
      long_description = "\n".join(doclines[2:]),
      classifiers =  """
      Development Status :: 3 - Alpha
      Environment :: Console
      License :: OSI Approved :: BSD License
      Intended Audience :: Developers
      Natural Language :: English
      Programming Language :: Python
      Operating System :: OS Independent
      Topic :: Text Processing""".strip().splitlines()
      )
