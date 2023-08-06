#
# Unit Tests for util/singleton
#
#

import os
import sys
from os.path import abspath, dirname
sys.path.insert(0, dirname(dirname(abspath(__file__)))+os.sep+".."+os.sep+"..")
currdir = dirname(abspath(__file__))+os.sep

import unittest
from nose.tools import nottest
import pyutilib


class A(pyutilib.MonoState):

    def __init__(self):
        self.state = True

class B(pyutilib.Singleton):

    def __init__(self):
        self.state = True
        

class SingletonDebug(unittest.TestCase):

    def test_A(self):
        """Verify that MonoState generates one global state"""
        a1 = A()
        a2 = A()
        self.failIfEqual(a1,a2)
        self.failUnlessEqual(a1.__dict__,a2.__dict__)

    def test_B(self):
        """Verify that Singleton generates one instance"""
        b1 = B()
        b2 = B()
        self.failUnlessEqual(b1,b2)

     
if __name__ == "__main__":
   unittest.main()
