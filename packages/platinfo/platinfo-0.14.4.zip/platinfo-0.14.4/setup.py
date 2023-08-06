#!/usr/bin/env python

"""platinfo: A small library from getting information on the current platform

This module determines and returns standardized names for
platforms, where the "standard" is Trent Mick's reasoning :)
from experience building ActivePython on a fairly large number of
platforms.

The driving goal is to provide platform names that are:
- relatively short
- readable (as much as possible making matching the given name to an
  actually machine self-explanatory)
- be capable enough to produce all names needed to distinguish all
  platform-specific application builds
- generally safe for usage in filenames
- not ugly (e.g. "MSWin32" is ugly)

A simple usage example:

>>> from platinfo import PlatInfo
>>> pi = PlatInfo()
>>> pi.os
'macosx'
>>> pi.arch
'x86'
>>> pi.name()
'macosx-x86'

Currently this has fairly wide OS coverage (Windows, Linux, Mac, Solaris,
HP-UX, AIX).
"""

import os
import sys
import distutils
from distutils.core import setup

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "lib"))
try:
    import platinfo
finally:
    del sys.path[0]

classifiers = """\
Development Status :: 5 - Production/Stable
Intended Audience :: Developers
License :: OSI Approved :: MIT License
Programming Language :: Python
Operating System :: OS Independent
Topic :: Software Development :: Libraries :: Python Modules
"""

if sys.version_info < (2, 3):
    # Distutils before Python 2.3 doesn't accept classifiers.
    _setup = setup
    def setup(**kwargs):
        if kwargs.has_key("classifiers"):
            del kwargs["classifiers"]
        _setup(**kwargs)

doclines = __doc__.split("\n")
script = (sys.platform == "win32" and "lib\\platinfo.py" or "bin/platinfo")

setup(
    name="platinfo",
    version=platinfo.__version__,
    maintainer="Trent Mick",
    maintainer_email="trentm@gmail.com",
    url="http://code.google.com/p/platinfo/",
    license="http://www.opensource.org/licenses/mit-license.php",
    platforms=["any"],
    py_modules=["platinfo"],
    package_dir={"": "lib"},
    scripts=[script],
    description=doclines[0],
    classifiers=filter(None, classifiers.split("\n")),
    long_description="\n".join(doclines[2:]),
)

