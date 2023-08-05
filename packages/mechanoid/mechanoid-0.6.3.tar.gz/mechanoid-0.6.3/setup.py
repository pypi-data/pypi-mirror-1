#!/usr/bin/env python

"""Python Programmatic Web Browser

mechanoid is a programmatic browser written in Python. It is intended as
an engine which will do things like log in as SourceForge project admin
and do a Quick Release or send and receive Yahoo mail.  mechanoid is a
fork of John J. Lee's mechanize.
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
NAME = "mechanoid"
PACKAGE = True
LICENSE = "GNU General Public License"
PLATFORMS = ["any"]
CLASSIFIERS = """\
Development Status :: 3 - Alpha
Environment :: Console
Intended Audience :: Developers
License :: OSI Approved :: GNU General Public License (GPL)
Natural Language :: English
Operating System :: OS Independent
Programming Language :: Python
Topic :: Internet
Topic :: Internet :: WWW/HTTP
Topic :: Internet :: WWW/HTTP :: Browsers
Topic :: Software Development :: Libraries
Topic :: Software Development :: Libraries :: Python Modules
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

packages = [
	NAME, NAME+".clientform",NAME+".clientform.formparser",
	NAME+".clientform.html_controls",NAME+".clientform.html_controls.alist",
	NAME+".cookiejar", NAME+".http_processors",
	NAME+".misc", NAME+".pullparser",
	NAME+".useragent", NAME+".useragent.http_handlers",
	NAME+".seek_wrapper", 	NAME+".sites",
			]
py_modules = None

doclines = string.split(__doc__, "\n")

setup(name = NAME,
      author = "Richard Harris",
      author_email = "richardharris@operamail.com",
      classifiers = filter(None, string.split(CLASSIFIERS, "\n")),
      description = doclines[0],
      license = LICENSE,
      long_description = string.join(doclines[2:], "\n"),
      packages = packages,
      platforms = PLATFORMS,
      py_modules = py_modules,
      url = "http://python.org/pypi/mechanoid",
      version = VERSION,
      )
