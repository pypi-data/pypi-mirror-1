#
# Unit Tests for util/*_io
#
#

import os
import sys
from os.path import abspath, dirname
sys.path.insert(0, dirname(dirname(abspath(__file__)))+os.sep+".."+os.sep+"..")
pkgdir = dirname(abspath(__file__))+os.sep+".."+os.sep+".."
currdir = dirname(abspath(__file__))+os.sep

import unittest
from nose.tools import nottest
import pyutilib
import pyutilib_th
import StringIO

class IODebug(pyutilib_th.TestCase):

    def test_redirect1(self):
        """Verify that IO redirection works"""
        pyutilib.setup_redirect(currdir+"redirect_io.out")
        print "HERE"
        print [1,2,3]
        #
        # Force a flush to ensure code coverage
        #
        sys.stdout.flush()
        pyutilib.reset_redirect()
        self.failUnlessFileEqualsBaseline(currdir+"redirect_io.out",currdir+"redirect_io1.txt")

    def test_redirect2(self):
        """Verify that IO redirection will create an empty file is no output is generated"""
        pyutilib.setup_redirect(currdir+"redirect_io.out")
        pyutilib.reset_redirect()
        if not os.path.exists(currdir+"redirect_io.out"):
            self.fail("Redirection did not create an empty file.")
        self.failUnlessFileEqualsBaseline(currdir+"redirect_io.out",currdir+"redirect_io2.txt")
    
    def test_redirect3(self):
        """Verify that IO redirection can be nested"""
        pyutilib.setup_redirect(currdir+"redirect_io1.out")
        print "HERE"
        pyutilib.setup_redirect(currdir+"redirect_io3.out")
        print "THERE"
        print [4,5,6]
        pyutilib.reset_redirect()
        print [1,2,3]
        #
        # Force a flush to ensure code coverage
        #
        sys.stdout.flush()
        pyutilib.reset_redirect()
        self.failUnlessFileEqualsBaseline(currdir+"redirect_io1.out",currdir+"redirect_io1.txt")
        self.failUnlessFileEqualsBaseline(currdir+"redirect_io3.out",currdir+"redirect_io3.txt")

    def test_redirect4(self):
        """Verify that IO redirection works with file-like objects"""
        output = StringIO.StringIO()
        pyutilib.setup_redirect(output)
        print "HERE"
        print [1,2,3]
        #
        # Force a flush to ensure code coverage
        #
        sys.stdout.flush()
        pyutilib.reset_redirect()
        self.failUnlessEqual(output.getvalue(),"HERE\n[1, 2, 3]\n")

    def test_format_io(self):
        """
        Test that formated IO looks correct.
        """
        pyutilib.setup_redirect(currdir+"format_io.out")
        print pyutilib.format_io(0.0)
        print pyutilib.format_io(0)
        print pyutilib.format_io(1e-1)
        print pyutilib.format_io(1e+1)
        print pyutilib.format_io(1e-9)
        print pyutilib.format_io(1e+9)
        print pyutilib.format_io(1e-99)
        print pyutilib.format_io(1e+99)
        print pyutilib.format_io(1e-100)
        print pyutilib.format_io(1e+100)
        print pyutilib.format_io(-1e-1)
        print pyutilib.format_io(-1e+1)
        print pyutilib.format_io(-1e-9)
        print pyutilib.format_io(-1e+9)
        print pyutilib.format_io(-1e-99)
        print pyutilib.format_io(-1e+99)
        print pyutilib.format_io(-1e-100)
        print pyutilib.format_io(-1e+100)
        print pyutilib.format_io('string')
        pyutilib.reset_redirect()
        self.failUnlessFileEqualsBaseline(currdir+"format_io.out",currdir+"format_io.txt")
        
    def test_format_float_err1(self):
        """ Test that errors are generated for non floats """
        try:
            pyutilib.format_float('1')
            self.fail("Should have thrown a TypeError exception")
        except TypeError:
            pass
        
        
if __name__ == "__main__":
   unittest.main()
