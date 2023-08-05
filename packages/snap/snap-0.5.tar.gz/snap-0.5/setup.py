##############################################################################
#
# Copyright (c) 2006 Zope Corporation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""snap - zope 3 frontend for entransit

provides some utilities for building websites the easy way with zope
3, wsgi, paste and some xslt.
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
from setuptools import setup, find_packages

# We're using the module docstring as the distutils descriptions.
doclines = __doc__.split("\n")
VERSION = "0.5"

setup(name="snap",
      version=VERSION,
      author="Sidnei da Silva",
      author_email="sidnei@enfoldsystems.com",
      keywords="web wsgi application server",
      url="http://cheeseshop.python.org/pypi/snap",
      download_url="http://cheeseshop.python.org/packages/source/s/snap/snap-%s.tar.gz" % VERSION,
      license="Lesser General Public License (LGPL)",
      platforms=["any"],
      description=doclines[0],
      classifiers=filter(None, classifiers.split("\n")),
      long_description="\n".join(doclines[2:]),
      packages=find_packages(exclude='tests dist build setup.py'),
      zip_safe=False,
      )
