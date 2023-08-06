#!/usr/bin/env python
#
# Copyright (c) 2007 Thomas Lotze
# See also LICENSE.txt

"""adpasswd.py Pure Python Command line interface to change Active Directory Passwords via LDAP.
	usage: adpasswd.py username [password]
"""

import os.path
import glob

from distutils.core import setup


longdesc = open("README.txt").read()

classifiers = [
    "Development Status :: 4 - Beta",
    "Environment :: Console",
    "Intended Audience :: Developers",
    "Intended Audience :: System Administrators",
	"Intended Audience :: Information Technology",
	"License :: OSI Approved :: GNU General Public License (GPL)",
    "Operating System :: OS Independent",
    "Programming Language :: Python",
	"Topic :: System :: Systems Administration",
	"Topic :: System :: Systems Administration :: Authentication/Directory",
	"Topic :: System :: Systems Administration :: Authentication/Directory :: LDAP",
	"Topic :: Utilities",
    ]

setup(name="adpasswd",
      version="0.2",
      description=__doc__.strip(),
      long_description=longdesc,
      keywords="ldap activedirectory AD",
      classifiers=classifiers,
      author="Craig Sawyer",
      author_email="csawyer@yumaed.org",
      url="https://launchpad.net/adpasswd",
      license="GPL v2",
	  py_modules=['ldaplib'],
	  scripts=['adpasswd.py']
      )
