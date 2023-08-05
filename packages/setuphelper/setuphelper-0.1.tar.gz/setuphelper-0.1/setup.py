#!/usr/bin/python -u
"""
Setup script for SetupHelper
Copyright (C) 2008 by Peter A. Donis

Released under the Python Software Foundation License.

This script is pleasantly multi-functional: it uses SetupHelper
itself (importing it from the setup directory) to set up SetupHelper
(installing it to site-packages, or your preferred module directory),
and also illustrates SetupHelper's intended use (though as this
is such a simple distribution, only some of the possible setup
variables are used here).
"""

import SetupHelper

__progname__ = "setuphelper"
__version__ = SetupHelper.SETUPHELPER_VERSION
__description__ = "A helper module for setup.py scripts."
__license__ = "PSF"
__author__ = "Peter A. Donis"
__author_email__ = "peterdonis@alum.mit.edu"
__url__ = "http://www.peterdonis.net"

# Unlike the normal case, we need to install ourselves!
__py_modules__ = ['SetupHelper']

__long_description__ = """
SetupHelper: Automating the Boilerplate in Python Setup Scripts
===============================================================

This Python module will make your setup scripts simpler to
write, by automating as much as possible of the 'boilerplate'
that normally goes into them. Instead of invoking the setup
function with a long list of keyword arguments, you just set
global variables in your setup script and then invoke the
setup_main function, passing globals() as its argument. (The
SetupHelper setup.py script itself illustrates this usage.)

The helper module does all the grunt work of translating your
variables into keyword arguments, including automatically
deducing and generating many arguments so that you only have
to specify a much simpler set of data. As a bonus, if you are
using Python's standard distutils, SetupHelper provides (very
basic!) support for the requires keyword, downloading and
installing required packages for you, as long as their download
URLs are available on PyPI. (Note that the distutils in Python
2.5 and later allow the requires keyword in distribution
metadata, but do not actually use it to install anything for
you. Of course some distutils replacements like setuptools do
provide this functionality; if you are using setuptools, you
can set the variable __distutils_pkg__ to 'setuptools' and
SetupHelper will use setuptools' support instead of its own.)

As one other bonus, SetupHelper allows you to automate the
running of post-install scripts; just set the __post_install__
variable in your setup.py to a list of script names to be run
from a subshell (this is done using os.system, so it has the
limitations of that Python command). It is desirable to allow
post-install scripts to be run from setup.py so that SetupHelper
can ensure that any required packages are fully installed by
just calling python setup.py install on them once they are
unpacked.

Installation
------------

Of course, to install SetupHelper, you can simply type

    $ python setup.py install

in the directory where you unpacked the SetupHelper archive.
However, since SetupHelper is used by setup scripts, you will
probably want to include it along with your setup.py in the
source archives for your Python projects.

Copyright and License
=====================

SetupHelper is Copyright (C) 2008 by Peter A. Donis. It is
released under the Python Software Foundation license, so
you can use and redistribute it just as you do Python itself.
"""

__classifiers__ = """
Development Status :: 3 - Alpha
Environment :: Console
Intended Audience :: Developers
Intended Audience :: System Administrators
License :: OSI Approved :: Python Software Foundation License
Operating System :: OS Independent
Programming Language :: Python
Topic :: Software Development :: Libraries :: Python Modules
Topic :: System :: Systems Administration
Topic :: Utilities
"""

if __name__ == '__main__':
    from SetupHelper import setup_main
    setup_main(globals())
