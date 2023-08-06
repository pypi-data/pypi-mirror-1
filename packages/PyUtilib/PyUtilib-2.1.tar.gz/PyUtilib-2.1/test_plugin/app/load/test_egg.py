#
# Plugin load tests for eggs
#

import os
import sys
from os.path import abspath, dirname
sys.path.insert(0, dirname(dirname(abspath(__file__)))+os.sep+".."+os.sep+"..")
currdir = dirname(abspath(__file__))+os.sep

import re
import unittest
from nose.tools import nottest
import pyutilib_th
import logging

try:
    import pkg_resources
    pkg_resources_avail=True
except ImportError:
    pkg_resources_avail=False
    

class TestEggLoader(pyutilib_th.TestCase):


    def run(self, result=None):
        global pkg_resources_avail
        if not pkg_resources_avail:
           return
        unittest.TestCase.run(self,result)

    def setUp(self):
        p = re.compile("pyutilib")
        global pyutilib
        pyutilib = __import__("pyutilib")
        pyutilib.plugin.PluginGlobals.push_env(pyutilib.plugin.PluginEnvironment("testing"))

    def tearDown(self):
        p = re.compile("pyutilib")
        pyutilib.plugin.PluginGlobals.pop_env()
        pyutilib.plugin.PluginGlobals.clear()
        tmp = []
        for item in sys.modules:
            if p.match(str(item)):
                tmp.append(str(item))
        for item in tmp:
            del sys.modules[item]
        if "test1" in sys.modules:
            del sys.modules["test1"]
        if "test2" in sys.modules:
            del sys.modules["test2"]
        if "test3" in sys.modules:
            del sys.modules["test3"]
        for item in sys.modules:
            if p.match(item):
                print item

    def test_egg1(self):
        """Load an egg for the 'project1' project.  Eggs are loaded in the 'eggs1' directory, but only the Project1 stuff is actually imported."""
        service = pyutilib.plugin.PluginFactory("EggLoader",namespace="project1")
        if service is None:
            self.fail("Cannot test the PyUtilib EggLoader Plugin on this system because the pkg_resources package is not available.")
        #
        #logging.basicConfig(level=logging.DEBUG)
        #
        pyutilib.plugin.PluginGlobals.env().load_services(path=currdir+"eggs1")
        #
        pyutilib.setup_redirect(currdir+"egg1.out")
        pyutilib.plugin.PluginGlobals.pprint(plugins=False, show_ids=False)
        #pyutilib.plugin.PluginGlobals.pprint()
        pyutilib.reset_redirect()
        self.failUnlessFileEqualsBaseline(currdir+"egg1.out", currdir+"egg1.txt")

    def test_egg2(self):
        """Load an egg for the 'project1' project.  Eggs are loaded in the 'eggs1' and 'eggs2' directories, but only the Project1 and Project 3 stuff is actually imported."""
        service = pyutilib.plugin.PluginFactory("EggLoader",namespace="project1")
        if service is None:
            self.fail("Cannot test the PyUtilib EggLoader Plugin on this system because the pkg_resources package is not available.")
        #
        #logging.basicConfig(level=logging.DEBUG)
        #
        pyutilib.plugin.PluginGlobals.env().load_services(path=[currdir+"eggs1", currdir+"eggs2"])
        #
        pyutilib.setup_redirect(currdir+"egg2.out")
        pyutilib.plugin.PluginGlobals.pprint(plugins=False, show_ids=False)
        #pyutilib.plugin.PluginGlobals.pprint()
        pyutilib.reset_redirect()
        self.failUnlessFileEqualsBaseline(currdir+"egg2.out", currdir+"egg2.txt")

if __name__ == "__main__":
   unittest.main()
