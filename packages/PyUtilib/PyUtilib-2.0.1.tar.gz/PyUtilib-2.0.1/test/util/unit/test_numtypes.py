#
# Unit Tests for numtypes
#
#

import os
import sys
from os.path import abspath, dirname
sys.path.insert(0, dirname(dirname(abspath(__file__)))+"/../..")

import unittest
from nose.tools import nottest
import pyutilib

class NumTypesDebug(unittest.TestCase):

    def test_infinity1(self):
        """Check that infinity is defined appropriately"""
        if 1 > pyutilib.infinity:
           self.fail("test_infinity")
        if not ((1.0/pyutilib.infinity) == 0.0):
           self.fail("test_infinity - 1/infinity is not zero")
        if pyutilib.is_finite(pyutilib.infinity):
           self.fail("test_infinity - infinity is finite")
        if pyutilib.is_finite(- pyutilib.infinity):
           self.fail("test_infinity - -infinity is finite")
        if not pyutilib.is_finite(1.0):
           self.fail("test_infinity - 1.0 is not finite")

    def test_nan(self):
        """Check that nan is defined appropriately"""
        if not type(pyutilib.nan) is type(1.0):
           self.fail("test_nan")
        if not pyutilib.is_nan(pyutilib.infinity/pyutilib.infinity):
           self.fail("test_nan - infinity/infinity is not NaN")
        if pyutilib.is_nan(1.0/pyutilib.infinity):
           self.fail("test_nan - 1.0/infinity is NaN")

if __name__ == "__main__":
   unittest.main()
