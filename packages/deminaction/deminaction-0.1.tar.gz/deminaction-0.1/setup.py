"""
deminaction - Python binding for "Democracy In Action" API

A thin pure Python wrapper over the demaction.org ("Democracy in
Action") web site, using their simple RESTful interface, which is
itself a very thin wrapper over an SQL database.
"""

classifiers = """\
Development Status :: 3 - Alpha
Environment :: Web Environment
License :: OSI Approved :: GNU Library or Lesser General Public License (LGPL)
Operating System :: OS Independent
Programming Language :: Python
Topic :: Internet :: WWW/HTTP
Topic :: Software Development :: Libraries :: Python Modules
"""

import os
import sys
from setuptools import setup

# We're using the module docstring as the distutils descriptions.
doclines = __doc__.split("\n")
VERSION = open('version.txt', 'rb').read().strip()

setup(name="deminaction",
      version=VERSION,
      author="J. Cameron Cooper",
      author_email="cameron@enfoldsystems.com",
      maintainer="Enfold Systems, LLC",
      maintainer_email="opensource@enfoldsystems.com",
      url = "http://enfoldsystems.com",
      license = "Lesser General Public License (LGPL)",
      platforms = ["any"],
      description = doclines[0],
      classifiers = filter(None, classifiers.split("\n")),
      long_description = "\n".join(doclines[2:]),
      packages = ['deminaction'],
      package_dir = {'deminaction': ''},
      )
