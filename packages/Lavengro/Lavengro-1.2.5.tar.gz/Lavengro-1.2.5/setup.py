#!/usr/bin/env python

"""Python Vocabulary Test Engine

Lavengro is a cross-platform, console-based vocabulary-test engine.  It
uses text files as its tests. The tests themselves are created by
you. It has a tutor mode, a test mode, and a CBT learning mode. 
There is also a bsd-quiz mode for nostalgia's sake.
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
NAME = "Lavengro"
PACKAGE = True
LICENSE = "GNU General Public License"
PLATFORMS = ["any"]
CLASSIFIERS = """\
Development Status :: 5 - Production/Stable
Environment :: Console
Intended Audience :: Education
License :: OSI Approved :: GNU General Public License (GPL)
Natural Language :: English
Operating System :: OS Independent
Programming Language :: Python
Topic :: Education
Topic :: Education :: Computer Aided Instruction (CAI)
Topic :: Education :: Testing
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

setup(name = "Lavengro",
	version = VERSION,
	license = LICENSE,
	platforms = PLATFORMS,
	classifiers = filter(None, string.split(CLASSIFIERS, "\n")),
	author = "Richard Harris",
	author_email = "richardharris@operamail.com",
	url = "http://python.org/pypi/Lavengro",
	description = doclines[0],
	long_description = string.join(doclines[2:], "\n"),
	py_modules = py_modules,
	packages = packages,
	)

