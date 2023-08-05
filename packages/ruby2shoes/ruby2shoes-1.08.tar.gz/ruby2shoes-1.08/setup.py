#!/usr/bin/env python

"""low-resource writer's software for screenplays and fiction

ruby2shoes combines Emacs and Python to create a sophisticated
writing environment for screenplay and fiction writers.  Emacs'
modes are used to create .sp or .fc files.  Spirit, a Python
application, then archives these files, converts them to text,
HTML or LaTeX, or prints them in a variety of ways.
"""

import sys, string
from distutils.core import setup

def get_version():
	f = open("version")
	tmp = f.readline()
	f.close()
	tokens = string.split(string.strip(tmp))
	ver = tokens[1]
	return ver

VERSION = get_version()
NAME = "ruby2shoes"
PACKAGE = True
LICENSE = "GNU General Public License"
PLATFORMS = ["any"]
CLASSIFIERS = """\
Development Status :: 5 - Production/Stable
Environment :: Console
Intended Audience :: End Users/Desktop
License :: OSI Approved :: GNU General Public License (GPL)
Natural Language :: English
Operating System :: OS Independent
Programming Language :: Python
Topic :: Text Editors :: Emacs
Topic :: Text Editors :: Text Processing
Topic :: Text Editors :: Word Processors
Topic :: Text Processing :: Markup :: HTML
Topic :: Text Processing :: Markup :: LaTeX
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
      version = 1.08,
      license = LICENSE,
      platforms = PLATFORMS,
      classifiers = filter(None, string.split(CLASSIFIERS, "\n")),
      author = "Ruby Dos Zapatas",
      author_email = "richardharris@operamail.com",
      description = doclines[0],
      url = "http://python.org/pypi/ruby2shoes",
      long_description = string.join(doclines[2:], "\n"),
      py_modules = py_modules,
      packages = packages,
      )
