#!/usr/bin/env python

"""Python Internet Programming Library

lib_rharris is a modest Python library for pulling,
parsing and pickling remote web page data and for
related net-aware tasks.
"""

import sys, string
from distutils.core import setup

def get_version():
	f = open("version")
	tmp = f.readline()
	f.close()
	tokens = string.split(tmp)
	ver = tokens[1]
	return ver

VERSION = get_version()
NAME = "lib_rharris"
PACKAGE = True
LICENSE = "GNU General Public License"
PLATFORMS = ["any"]
CLASSIFIERS = """\
Development Status :: 4 - Beta
Environment :: Console
Intended Audience :: Developers
License :: OSI Approved :: GNU General Public License (GPL)
Natural Language :: English
Operating System :: OS Independent
Programming Language :: Python
Topic :: Internet
Topic :: Internet :: File Transfer Protocol (FTP)
Topic :: Internet :: WWW/HTTP
Topic :: Software Development :: Libraries
Topic :: Software Development :: Libraries :: Python Modules
Topic :: Text Processing :: Markup :: HTML
Topic :: Utilities
"""

#-------------------------------------------------------
# the rest is constant for most of my released packages:

_setup = setup
def setup(**kwargs):
    if not hasattr(sys, "version_info") or sys.version_info < (2, 3):
        # Python version compatibility
        # XXX probably download_url came in earlier than 2.3
        for key in ["classifiers", "download_url"]:
            if kwargs.has_key(key):
                del kwargs[key]
    # Only want packages keyword if this is a package,
    # only want py_modules keyword if this is a single-file module,
    # so get rid of packages or py_modules keyword as appropriate.
    if kwargs["packages"] is None:
        del kwargs["packages"]
    else:
        del kwargs["py_modules"]
    apply(_setup, (), kwargs)

if PACKAGE:
    packages = [NAME]
    py_modules = None
else:
    py_modules = [NAME]
    packages = None

doclines = string.split(__doc__, "\n")

setup(name = NAME,
      author = "Richard Harris",
      author_email = "truenolejano@yahoo.com",
      classifiers = filter(None, string.split(CLASSIFIERS, "\n")),
      description = doclines[0],
      license = LICENSE,
      long_description = string.join(doclines[2:], "\n"),
      packages = packages,
      platforms = PLATFORMS,
      py_modules = py_modules,
      version = VERSION,
	  url = "http://cheeseshop.python.org",
      )
