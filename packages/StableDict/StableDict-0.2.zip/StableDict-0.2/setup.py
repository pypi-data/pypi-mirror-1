#! /usr/bin/env python
# setup.py,v 1.3 2007/08/28 09:46:31 martin Exp
#
# This is the StableDict setup script.
# This file is under the Python licence.
#
# 'python setup.py install', or
# 'python setup.py --help' for more options
#

"""A dictionary class remembering insertion order.

Order (i.e. the sequence) of insertions is remembered (internally
stored in a hidden list attribute) and replayed when iterating.  A
StableDict does NOT sort or organize the keys in any other way.

Implemented as a subclass of the builtin dict type.  Very compact
implementation (less than 150 lines of code).  Comes with a large
testsuite derived from Python's test_dict.py in a separate test
module.
"""

import sys

if not hasattr(sys, 'version_info') or sys.version_info < (2, 2):
    raise SystemExit, "StableDict requires Python 2.2 or later!"
if sys.version_info >= (3,):
    raise SystemExit, "StableDict requires Python 2.X!"

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

setup(name = 'StableDict',
      version = "0.2",
      author = 'Martin Kammerhofer',
      author_email = 'mkamm@gmx.net',
      # url =' XXX Should make up homepage!',
      description = 'A dict subclass which remembers insertion order',
      license = 'PSF',
      py_modules = ['stabledict', 'test_stabledict'],
      long_description = __doc__,
      platform = "any",
      # Extra attributes for setuptools below:
      zip_safe = True,
      test_suite = "test_stabledict.getTestSuite",
      )

#EOF#
