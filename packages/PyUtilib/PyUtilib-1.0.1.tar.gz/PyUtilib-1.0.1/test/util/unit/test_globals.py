#
# Unit Tests for util_globals
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
from pyutilib import Debug

class Globals(unittest.TestCase):

    def test_debug1(self):
        """Check that the debug function is False by default"""
        if pyutilib.debug():
           self.fail("test_debug1")

    def test_debug2(self):
        """Check that the debug function returns an exception for bad data"""
        try:
          foo=1
          pyutilib.debug(foo)
          self.fail("test_debug2")
        except pyutilib.BadDebuggingValue:
          pass

    def test_debug3(self):
        """Check that the debug always returns true if _Globals.debug is True"""
        pyutilib.config().debug=True
        if not pyutilib.debug():
           self.fail("test_debug3 - debug() is False")
        if not pyutilib.debug('quiet'):
           self.fail("test_debug3 - debug('quiet') is False")
        pyutilib.config().debug=[]

    def test_debug4(self):
        """Check that the debugging level can be set"""
        pyutilib.set_debugging('quiet')
        if not pyutilib.debug('quiet'):
           self.fail("test_debug4")
        pyutilib.config().debug=[]

    def test_debug5(self):
        """Check that the debugging level can be set"""
        pyutilib.set_debugging(Debug.quiet)
        if not pyutilib.debug(Debug.quiet):
           self.fail("test_debug5 - Debugging 'quiet' failed.")
        if pyutilib.debug():
           self.fail("test_debug5 - Debugging 'all' is not set.")
        pyutilib.config().debug=[]

    def test_debug6(self):
        """Check that the debugging level can be set"""
        pyutilib.set_debugging(Debug.quiet)
        if not pyutilib.debug(Debug.quiet):
           self.fail("test_debug6 - Debugging 'quiet' failed.")
        if pyutilib.debug():
           self.fail("test_debug6 - Debugging 'all' is not set.")
        pyutilib.config().debug=[]

    def test_debug7(self):
        """Check that an erroneous debugging level cannot be set"""
        try:
           pyutilib.set_debugging(1)
           self.fail("test_debug7 - can set a bad debugging value")
        except pyutilib.BadDebuggingValue:
           pass
        try:
           pyutilib.set_debugging("1")
           self.fail("test_debug7 - can set a bad debugging value")
        except pyutilib.BadDebuggingValue:
           pass
        pyutilib.config().debug=[]

    def test_debug8(self):
        """Check that an erroneous debugging level cannot be set"""
        pyutilib.set_debugging()
        if not pyutilib.debug(Debug.quiet):
           self.fail("test_debug8 - set 'all', so all debugging should be OK")
        pyutilib.config().debug=[]

    def test_config(self):
        """Check that we can set the global configuration"""
        pyutilib.config().debug=True
        tmp = pyutilib.Config()
        pyutilib.config(tmp)
        if pyutilib.config().debug == True:
           self.fail("test_config - setting the global configuration failed")

    def test_tempfile1(self):
        """Check that temporary files are added"""
        try:
          pyutilib.add_tempfile("foobar")
          self.fail("test_tempfile1")
        except IOError:
          pass

    def test_tempfile2(self):
        """Check that temporary files are added"""
        OUTPUT=open("tempfile2","w")
        print >>OUTPUT, "HERE"
        OUTPUT.close()
        pyutilib.add_tempfile("tempfile2")
        self.failUnlessEqual( len(pyutilib.util_globals._Globals._tempfiles), 1)
        pyutilib.remove_tempfiles()
        self.failUnlessEqual( len(pyutilib.util_globals._Globals._tempfiles), 0)
        if os.path.exists("tempfile2"):
           self.fail("tempfile2 - the file was not removed")

    def test_tempfile3(self):
        """Check that temporary files are added"""
        OUTPUT=open("tempfile3","w")
        print >>OUTPUT, "HERE"
        OUTPUT.close()
        pyutilib.add_tempfile("tempfile3")
        os.chdir("..")
        self.failUnlessEqual( len(pyutilib.util_globals._Globals._tempfiles), 1)
        pyutilib.remove_tempfiles()
        self.failUnlessEqual( len(pyutilib.util_globals._Globals._tempfiles), 0)
        os.chdir(currdir)
        if os.path.exists("tempfile3"):
           self.fail("tempfile2 - the file was not removed")

    def test_tempfile4(self):
        """Check that temporary files are added"""
        OUTPUT=open("tempfile4","w")
        print >>OUTPUT, "HERE"
        OUTPUT.close()
        pyutilib.add_tempfile("tempfile4")
        self.failUnlessEqual( len(pyutilib.util_globals._Globals._tempfiles), 1)
        os.remove("tempfile4")
        try:
          pyutilib.remove_tempfiles()
          self.fail("test_tempfile4")
        except IOError:
          pass

if __name__ == "__main__":
   unittest.main()
