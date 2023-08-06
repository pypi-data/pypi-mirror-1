#
# Unit Tests for util/math
#
#

import os
import sys
from os.path import abspath, dirname
sys.path.insert(0, dirname(dirname(abspath(__file__)))+"/../..")
cooprdir = dirname(abspath(__file__))+"/../.."

import unittest
from nose.tools import nottest
import pyutilib

class MathDebug(unittest.TestCase):

    def test_isint(self):
        """Verify that isint() identifies ints"""
        if pyutilib.isint([1,2]):
           self.fail("test_isint - thought that a list was an integer")
        if pyutilib.isint("a"):
           self.fail("test_isint - thought that a string was integer")
        if not pyutilib.isint(" 1 "):
           self.fail("test_isint - thought that an integer string was not an integer")
        if not pyutilib.isint(" 1.0 "):
           self.fail("test_isint - thought that an integer float string was not an integer")
        if pyutilib.isint(" 1.1 "):
           self.fail("test_isint - thought that a float string was an integer")
        if pyutilib.isint(1.1):
           self.fail("test_isint - thought that a float was integer")
        if not pyutilib.isint(1.0):
           self.fail("test_isint - thought that an integer float was not an integer")
        if not pyutilib.isint(1):
           self.fail("test_isint - thought that an integer was not an integer")

    def test_mean(self):
        """Verify that mean() works"""
        self.failUnlessEqual(pyutilib.mean((1,2,3)),2.0)
        try:
            val = pyutilib.mean([])
            self.fail("test_mean - should have failed with an empty list")
        except ArithmeticError:
            pass

    def test_median(self):
        """Verify that median() works"""
        self.failUnlessEqual(pyutilib.median((1,2,3)),2.0)
        self.failUnlessEqual(pyutilib.median((2,)),2.0)
        self.failUnlessEqual(pyutilib.median((1,2,3,4)),2.5)
        try:
            val = pyutilib.median([])
            self.fail("test_median - should have failed with an empty list")
        except ArithmeticError:
            pass

    def test_factorial(self):
        """Verify that factorial() works"""
        self.failUnlessEqual(pyutilib.factorial(0),1)
        self.failUnlessEqual(pyutilib.factorial(1),1)
        self.failUnlessEqual(pyutilib.factorial(2),2)
        self.failUnlessEqual(pyutilib.factorial(3),6)
        self.failUnlessEqual(pyutilib.factorial(4),24)
        try:
            val = pyutilib.factorial(-1)
            self.fail("test_factorial - should have failed with a negative value")
        except ArithmeticError:
            pass
        

    def test_perm(self):
        """Verify that perm() works"""
        self.failUnlessEqual(pyutilib.perm(7,1),7)
        self.failUnlessEqual(pyutilib.perm(7,2),21)

if __name__ == "__main__":
   unittest.main()
