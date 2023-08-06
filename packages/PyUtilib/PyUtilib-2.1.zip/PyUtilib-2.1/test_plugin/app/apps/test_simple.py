#
# Test simple applications
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

def do_setUp():
        p = re.compile("pyutilib")
        global pyutilib
        pyutilib = __import__("pyutilib")
        pyutilib.plugin.PluginGlobals.push_env(pyutilib.plugin.
PluginEnvironment())

def do_tearDown():
        p = re.compile("pyutilib")
        pyutilib.plugin.PluginGlobals.pop_env()
        pyutilib.plugin.PluginGlobals.clear()
        tmp = []
        for item in sys.modules:
            if p.match(str(item)):
                tmp.append(str(item))
        for item in tmp:
            del sys.modules[item]


class Test(pyutilib_th.TestCase):

    def setUp(self):
        do_setUp()

    def tearDown(self):
        do_tearDown()

    def test_app1(self):
        app=pyutilib.plugin.SimpleApplication("foo")
        #pyutilib.plugin.PluginGlobals.pprint()
        app._env_config.options.path = "DEFAULT PATH HERE"
        app.config.save(currdir+"config1.out")
        self.failUnlessFileEqualsBaseline(currdir+"config1.out", currdir+"config1.txt")
        app.config.load(currdir+"config1.txt")
        app.config.save(currdir+"config1.out")
        self.failUnlessFileEqualsBaseline(currdir+"config1.out", currdir+"config1.txt")

    def test_app2(self):
        app=pyutilib.plugin.SimpleApplication("foo")
        #pyutilib.plugin.PluginGlobals.pprint()
        pyutilib.setup_redirect(currdir+"summary.out")
        app.config.summarize()
        pyutilib.reset_redirect()
        self.failUnlessFileEqualsBaseline(currdir+"summary.out", currdir+"summary.txt")

    def test_app3(self):
        #if os.path.exists(currdir+"app3.log"):
            #os.remove(currdir+"app3.log")
        app=pyutilib.plugin.SimpleApplication("foo")
        app.config.load(currdir+"log1.ini")
        app.logger.log_dir = currdir
        app.logger.log_file = "app3.log"
        app.logger.reset_after_updates()
        app.env.load_services()
        app.log("test_app3 message")
        app.flush()
        if not os.path.exists(currdir+"app3.log"):
            self.fail("expected log file")

    def test_app4(self):
        app=pyutilib.plugin.SimpleApplication("foo")
        app.config.load(currdir+"log1.ini")
        #print type(app.logger.log_dir)
        app.logger.log_dir = currdir
        #print type(app.logger.log_dir)
        app.config.save(currdir+"tmp2.ini")

if __name__ == "__main__":
   unittest.main()
