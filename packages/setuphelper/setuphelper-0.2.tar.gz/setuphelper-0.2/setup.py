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

# This is a tuple, SetupHelper will automatically convert it to a string.
__version__ = SetupHelper.SETUPHELPER_VERSION

# This will automatically insert the appropriate classifier, so we don't
# need to include one for development status below; note that it's in
# all lowercase to test the case-insensitivity of the automatic check
__dev_status__ = 'alpha'

__description__ = "A helper module for setup.py scripts."

# These tell SetupHelper where to look in README for the long description.
__start_line__ = "SetupHelper: Automating Boilerplate in Python Setup Scripts"
__end_line__ = "Copyright and License"

__license__ = "PSF"
__author__ = "Peter A. Donis"
__author_email__ = "peterdonis@alum.mit.edu"
__url__ = "http://www.peterdonis.net"

# These are files in the setup directory that should be included in MANIFEST.in
# (distutils always includes setup.py and README, and SetupHelper always adds
# itself, so you don't have to list those).
__rootfiles__ = ["CHANGES"]

# Normally SetupHelper.py is excluded from auto-detection of pure Python modules
# in the setup directory; however, unlike the normal case, we need to install
# ourselves! Hence, we manually override the normal behavior here.
__py_modules__ = ['SetupHelper']

# SetupHelper will automatically convert this to a list.
__classifiers__ = """
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

# We don't need to specify __download_url__ if we specify __url_base__
# and either __url_type__ or __url_ext__; but since here we are OK with
# the defaults for those (the PyPI base URL and a .tar.gz extension),
# we don't need to define anything.

# This stanza is normally all you need to do once variables are defined.
if __name__ == '__main__':
    from SetupHelper import setup_main
    setup_main(globals())
