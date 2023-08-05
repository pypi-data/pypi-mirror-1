#!/usr/bin/env python
"""VObject: module for reading vCard and vCalendar files

Requires dateutil (https://moin.conectiva.com.br/DateUtil) 0.9 or later.
"""

from distutils.core import setup

classifiers = """\
Development Status :: 3 - Alpha
Environment :: Console
License :: OSI Approved :: BSD License
Programming Language :: Python
Operating System :: OS Independent
Topic :: Text Processing
"""

doclines = __doc__.split("\n")

setup(name = "vobject",
      version = "0.2.3",
      author = "Jeffrey Harris",
      author_email = "jeffrey-osaf@skyhouseconsulting.com",
      license = "BSD",
      url = "http://vobject.skyhouseconsulting.com",
      platforms = ["any"],
      packages = ["vobject"],
      description = doclines[0],
      long_description = "\n".join(doclines[2:]),
      classifiers = filter(None, classifiers.split("\n")),
      )
