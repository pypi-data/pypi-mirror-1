#
# Plugin load tests, with the sys.path loader disabled.
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


class TestLoader(pyutilib_th.TestCase):


    def setUp(self):
        p = re.compile("pyutilib")
        global pyutilib
        pyutilib = __import__("pyutilib")
        #pyutilib.plugin.TempfileManagerPlugin()
        #pyutilib.plugin.PluginGlobals.push_env(pyutilib.plugin.PluginEnvironment("testing"))

    def tearDown(self):
        p = re.compile(".*pyutilib.*")
        #pyutilib.plugin.PluginGlobals.pop_env()
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

    def test_load1(self):
        #logging.basicConfig(level=logging.DEBUG)
        pyutilib.plugin.PluginGlobals.env().load_services(path=currdir+"plugins1")
        pyutilib.setup_redirect(currdir+"load1.out")
        pyutilib.plugin.PluginGlobals.pprint(plugins=False, show_ids=False)
        pyutilib.reset_redirect()
        self.failUnlessFileEqualsBaseline(currdir+"load1.out", currdir+"load1.txt")

    def test_load1a(self):
        pyutilib.plugin.PluginGlobals.env().load_services(path=currdir+"plugins1", auto_disable=True)
        pyutilib.setup_redirect(currdir+"load1a.out")
        pyutilib.plugin.PluginGlobals.pprint(plugins=False, show_ids=False)
        pyutilib.reset_redirect()
        self.failUnlessFileEqualsBaseline(currdir+"load1a.out", currdir+"load1a.txt")

    def test_load2(self):
        pyutilib.plugin.PluginGlobals.env().load_services(path=[currdir+"plugins1", currdir+"plugins2"])
        pyutilib.setup_redirect(currdir+"load2.out")
        pyutilib.plugin.PluginGlobals.pprint(plugins=False, show_ids=False)
        pyutilib.reset_redirect()
        #pyutilib.plugin.PluginGlobals.pprint()
        self.failUnlessFileEqualsBaseline(currdir+"load2.out", currdir+"load2.txt")

    def test_load2a(self):
        pyutilib.plugin.PluginGlobals.env().load_services(path=[currdir+"plugins1", currdir+"plugins2"], auto_disable=True)
        pyutilib.setup_redirect(currdir+"load2a.out")
        pyutilib.plugin.PluginGlobals.pprint(plugins=False, show_ids=False)
        pyutilib.reset_redirect()
        #pyutilib.plugin.PluginGlobals.pprint()
        self.failUnlessFileEqualsBaseline(currdir+"load2a.out", currdir+"load2a.txt")

if __name__ == "__main__":
   unittest.main()
