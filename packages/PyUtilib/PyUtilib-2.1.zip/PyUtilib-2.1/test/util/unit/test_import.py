#
# Unit Tests for util/misc/import_file
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

try:
   import runpy
   _runpy=True
except:
   _runpy=False

class DebugImport(pyutilib_th.TestCase):

    def run(self, result=None):
        """ Disable the tests if runpy is not available """
        if not _runpy:
           return
        unittest.TestCase.run(self,result)

    def test_import_file(self):
        pyutilib.import_file(currdir+"import1.py")
        if "import1" in globals():
           self.fail("test_import_file - globals() should not be affected by import")
        import1 = pyutilib.import_file(currdir+"import1.py")
        try:
           c = import1.a
        except:
           self.fail("test_import_file - could not access data in import.py")
        pyutilib.import_file(currdir+"import1.py", context=globals())
        if not "import1" in globals():
           self.fail("test_import_file - failed to import the import1.py file")

    def test_run_file1(self):
        pyutilib.run_file(currdir+"import1.py", logfile=currdir+"import1.log")
        if not os.path.exists(currdir+"import1.log"):
           self.fail("test_run_file - failed to create logfile")
        self.failUnlessFileEqualsBaseline(currdir+"import1.log",currdir+"import1.txt")
        
    def test_run_file2(self):
        pyutilib.run_file("import1.py", logfile=currdir+"import1.log", execdir=currdir)
        if not os.path.exists(currdir+"import1.log"):
           self.fail("test_run_file - failed to create logfile")
        self.failUnlessFileEqualsBaseline(currdir+"import1.log",currdir+"import1.txt")
        
    def test_run_file3(self):
        try:
           pyutilib.run_file("import2.py", logfile=currdir+"import2.log", execdir=currdir)
           self.fail("test_run_file - expected type error in import2.py")
        except TypeError:
           pass
        self.failUnlessFileEqualsBaseline(currdir+"import2.log",currdir+"import2.txt")
        

if __name__ == "__main__":
   unittest.main()
