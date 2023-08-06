#!/usr/bin/env python
# setup.py
# Distutils setup for the pythonutils package.
# Uses some of the buildutils commands.

# Copyright Michael Foord 2005-07
# EMail: fuzzyman AT voidspace DOT org DOT uk

# Released subject to the BSD License
# Please see http://www.voidspace.org.uk/python/license.shtml

# Scripts maintained at http://www.voidspace.org.uk/python/index.shtml
# For information about bugfixes, updates and support, please join the
# ConfigObj mailing list:
# http://lists.sourceforge.net/lists/listinfo/configobj-develop
# Comments, suggestions and bug reports welcome.

import sys
from distutils.core import setup
try:
    import buildutils
except ImportError:
    pass

NAME = 'configobj'
DESCRIPTION = 'Config file reading, writing and validation.'
URL = 'http://www.voidspace.org.uk/python/configobj.html'
LICENSE = 'BSD License'
PLATFORMS = ['Platform Independent']
VERSION = '4.5.3'
py_modules = ['configobj']

setup(name= NAME,
      version = VERSION,
      description = DESCRIPTION,
      license = LICENSE,
      platforms = PLATFORMS,
      author = 'Michael Foord',
      author_email = 'fuzzyman@voidspace.org.uk',
      url = URL,
      py_modules = py_modules
     )

