#!/usr/bin/env python

"""A Honking-good Little Python Application Server

Maybe you'd like a server that gives you control of your site, that
keeps its own log, a server that serves HTML, pre-formatted text, or the
output of any Python code wrapped in a data page.  That's what The Ming
Server does.  And it is the basis for the MingMods which connect your
content to your PayPal account and for MingZine which lets you publish
other people this way and take a percentage of their direct sales.
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
NAME = "TheMingServer"
PACKAGE = True
LICENSE = "GNU General Public License"
PLATFORMS = ["any"]
CLASSIFIERS = """\
Development Status :: 4 - Beta
Environment :: Web Environment
Intended Audience :: Developers
Intended Audience :: End Users/Desktop
Intended Audience :: System Administrators
License :: OSI Approved :: GNU General Public License (GPL)
Natural Language :: English
Operating System :: OS Independent
Programming Language :: Python
Topic :: Internet :: WWW/HTTP :: Dynamic Content
Topic :: Internet :: WWW/HTTP :: Site Management
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
      version = VERSION,
      license = LICENSE,
      platforms = PLATFORMS,
      classifiers = filter(None, string.split(CLASSIFIERS, "\n")),
      author = "Billy Bob Ming",
      author_email = "billy_bob_ming@yahoo.com",
      description = doclines[0],
      url = "http://python.org/pypi/TheMingServer",
      long_description = string.join(doclines[2:], "\n"),
      py_modules = py_modules,
      packages = packages,
      )
