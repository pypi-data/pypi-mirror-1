#
# Unit Tests for util/math
#
#

import os
import sys
import warnings
from os.path import abspath, dirname
sys.path.insert(0, dirname(dirname(abspath(__file__)))+"/../..")
pkgdir = dirname(abspath(__file__))+"/../.."
currdir = dirname(abspath(__file__))+os.sep

import unittest
from nose.tools import nottest
import pyutilib

class TestPlugin1(pyutilib.ConfigPlugin):

    def __init__(self):
        pyutilib.ConfigPlugin.__init__(self)

    def add_options(self, parser):
        parser.add_option(
            "--plugin", action="store", dest="plugin", default="none")
        return "PluginSection",["plugin"]
    
    def configure(self, options, config):
        self.plugin_value = options.plugin

class TestPlugin2(pyutilib.ConfigPlugin):

    def __init__(self):
        pyutilib.ConfigPlugin.__init__(self)

    def add_options(self, parser):
        parser.add_option(
            "--plugin2", action="store", dest="plugin2", default="none")
        return "PluginSection",["plugin2"]
    
    def configure(self, options, config):
        self.plugin_value = options.plugin2

class TestPlugin3(pyutilib.ConfigPlugin):

    def __init__(self):
        pyutilib.ConfigPlugin.__init__(self)

    def add_options(self, parser):
        parser.add_option(
            "--plugin3", action="store", dest="plugin3", default="none")
        return "PluginSection",["plugin3", "plugin4" ] # ERROR
    
    def configure(self, options, config):
        self.plugin_value = options.plugin3

class DerivedConfig(pyutilib.Config):

    def __init__(self,**kw):
        pyutilib.Config.__init__(self,**kw)

    def _getParser(self, doc=None):
        pyutilib.Config._getParser(self,doc)
        self._parser.add_option(
            "--f1", action="store_true", dest="f1", default=False)
        self._parser.add_option(
            "--f2", action="store_true", dest="f2", default=False)
        self._parser.add_option(
            "--f3", action="store_true", dest="f3", default=False)
        self._parser.add_option(
            "--f4", action="store_true", dest="f4", default=False)
        self._parser.add_option(
            "--f5", action="store_true", dest="f5", default=False)
        self._parser.add_option(
            "--f6", action="store_true", dest="f6", default=False)
        self._parser.add_option(
            "--f7", action="store_true", dest="f7", default=False)
        self._parser.add_option(
            "--f8", action="store_true", dest="f8", default=False)
        self._parser.add_option(
            "--f9", action="store_true", dest="f9", default=False)
        self._parser.add_option(
            "--f10", action="store_true", dest="f10", default=False)
        self._parser.add_option(
            "--f11", action="store_true", dest="f11", default=False)
        self._parser.add_option(
            "--f12", action="store_true", dest="f12", default=False)
        self._sections["bools"] = ["f1","f2","f3","f4","f5","f6","f7","f8","f9","f10","f11","f12"]
        return self._parser

class ConfigDebug(unittest.TestCase):

    def setUp(self):
        self.config = pyutilib.Config()
        self.config.configure(files=currdir+"setup.cfg")

    def test_str(self):
        """ Verify that we can generate string representations """
        self.failUnlessEqual( str(self.config), "Config(debug=[], files=[], tempdir='/foobar')")

    def test_write(self):
        """ Verify that we can write to a file """
        OUTPUT=open("test_config.tmp","w")
        self.config.write(OUTPUT)
        OUTPUT.close()
        tmp=""
        INPUT=open("test_config.tmp")
        for line in INPUT:
          tmp=tmp+line
        INPUT.close()
        ans="[globals]\ndebug=[]\nfiles=[]\ntempdir=/foobar\n"
        self.failUnlessEqual( tmp, ans )
        os.remove("test_config.tmp")
        
    def test_write2(self):
        """ Verify that we can write to a file """
        #
        # This is like test_write2, except that we redirect stdout
        #
        OUTPUT=open("test_config.tmp","w")
        tmp = sys.stdout
        sys.stdout=OUTPUT
        self.config.write()
        sys.stdout=tmp
        OUTPUT.close()
        tmp=""
        INPUT=open("test_config.tmp")
        for line in INPUT:
          tmp=tmp+line
        INPUT.close()
        ans="[globals]\ndebug=[]\nfiles=[]\ntempdir=/foobar\n"
        self.failUnlessEqual( tmp, ans )
        os.remove("test_config.tmp")
        
    def test_load(self):
        """ Verify that we can have config files load other config files """
        self.config = pyutilib.Config()
        self.config.configure(files=currdir+"test1.cfg")
        # Reconfigure to force some coverage of config.py
        self.config.configure(files=currdir+"test1.cfg")
        self.failUnlessEqual( str(self.config), "Config(debug=[], files=[], tempdir='/test2')")
        
    def test_load_bad1(self):
        """ Verify that we get a warning for a unknown filename"""
        self.config = pyutilib.Config()
        warnings.filterwarnings("error",category=RuntimeWarning)
        try:
           self.config.configure(files=currdir+"bad.cfg")
           self.fail("test_load_bad")
        except RuntimeWarning:
           pass
        warnings.filterwarnings("default",category=RuntimeWarning)
        
    def test_load_bad2(self):
        """ Verify that we get a warning for a badly formated file"""
        self.config = pyutilib.Config()
        warnings.filterwarnings("error",category=RuntimeWarning)
        try:
           self.config.configure(files=currdir+"test3.cfg")
           self.fail("test_load_bad")
        except RuntimeWarning:
           pass
        warnings.filterwarnings("default",category=RuntimeWarning)
        
    def test_load_bad3(self):
        """ Verify that we ignore data when the 'globals' section is not there """
        self.config = pyutilib.Config()
        self.config.configure(files=currdir+"test4.cfg")
        
    def test_load_bad4(self):
        """ Verify that we get a warning for an unexpected option"""
        self.config = pyutilib.Config()
        warnings.filterwarnings("error",category=RuntimeWarning)
        try:
           self.config.configure(files=currdir+"test10.cfg")
           self.fail("test_load_bad")
        except RuntimeWarning:
           pass
        warnings.filterwarnings("default",category=RuntimeWarning)
        
    def test_default(self):
        """ Verify that default resets the config """
        self.config.default()
        self.failUnlessEqual( self.config._parser, None)

    def test_reset(self):
        """ Verify that default resets the config """
        self.config = pyutilib.Config(blah=1)
        self.config.configure(files=currdir+"setup.cfg")
        self.config.reset()
        self.config.tempdir=''
        self.failUnlessEqual( str(self.config), "Config(blah=1, debug=[], files=[], tempdir='')")

    def test_bools(self):
        """ Verify that boolean values are set appropriately"""
        self.config = DerivedConfig()
        self.config.configure(files=currdir+"test5.cfg")
        #self.failUnlessEqual( self.config._options.f1, True)
        #self.failUnlessEqual( self.config._options.f2, False)
        self.failUnlessEqual( self.config._options.f3, False)
        self.failUnlessEqual( self.config._options.f4, True)
        self.failUnlessEqual( self.config._options.f5, True)
        self.failUnlessEqual( self.config._options.f6, False)
        self.failUnlessEqual( self.config._options.f7, True)
        self.failUnlessEqual( self.config._options.f8, False)
        self.failUnlessEqual( self.config._options.f9, True)
        self.failUnlessEqual( self.config._options.f10, False)
        self.failUnlessEqual( self.config._options.f11, True)
        self.failUnlessEqual( self.config._options.f12, False)

    def test_debug1(self):
        """ Verify that debugging flags get set properly"""
        self.config = pyutilib.Config()
        self.config.configure(files=currdir+"test6.cfg")
        self.failUnlessEqual( str(self.config), "Config(debug=[quiet], files=[], tempdir='/test6')")
        
    def test_debug2(self):
        """ Verify that debugging flags get set properly with multiple debugging levels"""
        self.config = pyutilib.Config()
        self.config.configure(files=currdir+"test7.cfg")
        self.failUnlessEqual( str(self.config), "Config(debug=[verbose,normal], files=[], tempdir='/test7')")
        
    def test_debug3(self):
        """ Verify that debugging flags get set properly with a bad debugging level"""
        self.config = pyutilib.Config()
        try:
          self.config.configure(files=currdir+"test8.cfg")
          self.fail("test_debug3")
        except pyutilib.BadDebuggingValue:
          pass
        
    def test_plugin(self):
        """ Verify we can register plugins """
        self.config = pyutilib.Config()
        plugin = TestPlugin1()
        self.config.add_plugin(plugin)
        plugin2 = TestPlugin2()
        self.config.add_plugin(plugin2)
        self.config.configure(files=currdir+"test9.cfg")
        self.failUnlessEqual( str(self.config), "Config(debug=[], files=[], tempdir='/test9')\nConfigPlugin(plugin_value='test')\nConfigPlugin(plugin_value='test2')")

    def test_bad_plugin(self):
        """ Verify we can get an error for a bad plugin registeration """
        self.config = pyutilib.Config()
        plugin = TestPlugin3()
        self.config.add_plugin(plugin)
        try:
          self.config.configure(files=currdir+"test9.cfg")
          self.fail("test_bad_plugin")
        except ValueError:
          pass

if __name__ == "__main__":
   unittest.main()
