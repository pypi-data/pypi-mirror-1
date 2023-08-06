#
# Unit Tests for pyutilib.plugin_core.options
#
#

import os
import sys
from os.path import abspath, dirname
sys.path.insert(0, dirname(dirname(abspath(__file__)))+os.sep+".."+os.sep+"..")
currdir = dirname(abspath(__file__))+os.sep

import unittest
from nose.tools import nottest
from pyutilib.plugin import *


class TestOption(unittest.TestCase):

    def setUp(self):
        PluginGlobals.push_env(PluginEnvironment())

    def tearDown(self):
        PluginGlobals.clear()

    def test_init1(self):
        """Test Option construction"""
        try:
            Option()
            self.fail("expected failure")
        except OptionError:
            pass

        try:
            Option(None)
            self.fail("expected failure")
        except OptionError:
            pass

        try:
            Option("name",x=None)
            self.fail("expected failure")
        except OptionError:
            pass

    def test_init2(self):
        """Test Option construction"""
        FOO = Option("foo")
        self.failUnlessEqual(FOO.name,"foo")
        self.failUnless(FOO.default is None)
        self.failUnless(FOO.section == "globals")
        self.failUnless(FOO.section_re == None)
        self.failUnless(FOO.__doc__ == "")

    def test_init3(self):
        """Test Option construction"""
        FOO = Option(name="foo", default=1, section="a", doc="b", section_re="re")
        self.failUnlessEqual(FOO.name,"foo")
        self.failUnlessEqual(FOO.default, 1)
        self.failUnless(FOO.get_value() == 1)
        self.failUnlessEqual(FOO.section, "a")
        self.failUnlessEqual(FOO.section_re, "re")
        self.failUnlessEqual(FOO.__doc__, "b")

    def test_set_get1(self):
        """Test set/get values"""
        class TMP(Plugin):
            ep = ExtensionPoint(IOption)
            declare_option("foo", local_name="opt", default=4)
        obj = TMP()
        self.failUnless(obj.opt/2 == 2)
        obj.opt = 6
        self.failUnless(obj.opt/2 == 3)
        #
        # Verify that the TMP instance has value 6
        #
        #PluginGlobals.pprint()
        for pt in obj.ep:
            self.failUnlessEqual(pt.get_value(),6)

    def test_set_get2(self):
        """Test validate global nature of set/get"""
        class TMP(Plugin):
            ep = ExtensionPoint(IOption)
            declare_option("foo", local_name="o1", default=4)
            declare_option("foo", local_name="o2", default=4)
        obj = TMP()
        self.failUnlessEqual(type(obj.o1), int)
        self.failUnless(obj.o1/2 == 2)
        obj.o1 = 6
        self.failUnless(obj.o1/2 == 3)
        self.failUnless(obj.o2/2 == 3)

    def test_set_get3(self):
        """Test validate nature of set/get for instance-specific options"""
        class TMP(Plugin):
            ep = ExtensionPoint(IOption)
            def __init__(self, section):
                declare_option("o1", section=section, default=4)
        obj1 = TMP("sec1")
        obj2 = TMP("sec1")
        obj3 = TMP("sec2")
        self.failUnlessEqual(type(obj1.o1), int)
        self.failUnless(obj1.o1/2 == 2)
        self.failUnless(obj2.o1/2 == 2)
        self.failUnless(obj3.o1/2 == 2)
        obj1.o1 = 6
        self.failUnless(obj1.o1/2 == 3)
        self.failUnless(obj2.o1/2 == 3)
        self.failUnless(obj3.o1/2 == 2)

    def test_repr(self):
        """Test string repn"""
        ep = ExtensionPoint(IOption)
        class TMP(Plugin):
            declare_option("o1", default=4)
            declare_option("o2", section="foo", default=4)
        obj = TMP()
        if re.match("\<Option \[globals\] 'o1'\>",str(ep.service("o1"))) is None:
            self.fail("Expected globals:o1, but this option is %s" % str(ep.service("o1")))
        self.failIf(re.match("\<Option \[globals\] 'o1'\>",str(ep.service("o1"))) is None)
        self.failIf(re.match("\<Option \[foo\] 'o2'\>",str(ep.service("o2"))) is None)
        self.failUnlessEqual(ep.service("o1").get_value(),4)
        ep.service("o1").load("o1",["new"])
        self.failUnlessEqual(ep.service("o1").get_value(),"new")
        ep.service("o1").load("o1","old")
        self.failUnlessEqual(ep.service("o1").get_value(),"old")

    def test_bool(self):
        """Test boolean"""
        ep = ExtensionPoint(IOption)
        class TMP(Plugin):
            declare_option("o1", cls=BoolOption)
        obj = TMP()
        pt = ep.service("o1")

        pt.load("o1",[True])
        self.failUnlessEqual(pt.get_value(),True)
        
        pt.load("o1",[False])
        self.failUnlessEqual(pt.get_value(),False)

        pt.load("o1",[1])
        self.failUnlessEqual(pt.get_value(),True)
        
        pt.load("o1",[0])
        self.failUnlessEqual(pt.get_value(),False)

        pt.load("o1",['YES'])
        self.failUnlessEqual(pt.get_value(),True)
        
        pt.load("o1",['no'])
        self.failUnlessEqual(pt.get_value(),False)

    def test_int(self):
        """Test int"""
        ep = ExtensionPoint(IOption)
        class TMP(Plugin):
            declare_option("o1",cls=IntOption)
        obj = TMP()
        pt = ep.service("o1")

        pt.load("o1",[-1])
        self.failUnlessEqual(pt.get_value(),-1)
        
        pt.load("o1",["-1"])
        self.failUnlessEqual(pt.get_value(),-1)

        pt.load("o1",[[]])
        self.failUnlessEqual(pt.get_value(),0)

        try:
            pt.load("o1",[['a']])
            self.fail("expected error")
        except OptionError:
            pass
        
        try:
            pt.load("o1",["-1.5"])
            self.fail("expected error")
        except OptionError:
            pass
        
    def test_float(self):
        """Test float"""
        ep = ExtensionPoint(IOption)
        class TMP(Plugin):
            declare_option("o1",cls=FloatOption)
        obj = TMP()
        pt = ep.service("o1")

        pt.load("o1",[-1.5])
        self.failUnlessEqual(pt.get_value(),-1.5)
        
        pt.load("o1",["-1.5"])
        self.failUnlessEqual(pt.get_value(),-1.5)

        pt.load("o1",[[]])
        self.failUnlessEqual(pt.get_value(),0)

        try:
            pt.load("o1",[['a']])
            self.fail("expected error")
        except OptionError:
            pass
        
        try:
            pt.load("o1",['a'])
            self.fail("expected error")
        except OptionError:
            pass
        
    def test_dict1(self):
        """Test DictOption"""
        ep = ExtensionPoint(IOption)
        class TMP(Plugin):
            declare_option("options", DictOption)
            declare_option("b")
            declare_option("c", default=3)
        obj = TMP()

        self.failUnlessEqual(obj.options.b,None)
        self.failUnlessEqual(obj.options.c,3)

    def test_dict2(self):
        """Test DictOption"""
        ep = ExtensionPoint(IOption)
        class TMP(Plugin):
            declare_option("options",DictOption)
            declare_option("b", local_name="o1")
            declare_option("c", local_name="o2", default=3)
        obj = TMP()
        #
        # testing attribute set/get
        #
        obj.options.x = 3
        self.failUnlessEqual(obj.options.x,3)
        try:
            obj.options.xx
            self.fail("expected error")
        except OptionError:
            pass
        #
        # Testing the DictOption set/get
        #
        obj.options = {'yy':3, 'zz':2}
        self.failUnlessEqual(obj.options.yy,3)
        self.failUnlessEqual(obj.options.zz,2)
        #
        # Testing load
        #
        #obj.options.load('vv',1)
        #obj.options.load('uu',[1])
        #self.failUnlessEqual(obj.options.uu,3)
        #self.failUnlessEqual(obj.options.vv,3)

    def test_path(self):
        """Test path"""
        ep = ExtensionPoint(IOption)
        if sys.platform == "win32":
            o1_default = "C:/default"
        else:
            o1_default = "/dev//default"
        class TMP(Plugin):
            declare_option("o1",cls=FileOption,default=o1_default, directory="/dev/null")
        obj = TMP()
        pt = ep.service("o1")

        pt.load("o1",[None])
        if sys.platform == "win32":
            self.failUnlessEqual(pt.get_value(),"c:\\default")
        else:
            self.failUnlessEqual(pt.get_value(),"/dev/default")
        
        if sys.platform == "win32":
            pt.load("o1",["C:/load1"])
        else:
            pt.load("o1",["/dev/load1"])
        if sys.platform == "win32":
            self.failUnlessEqual(pt.get_value(),"c:\\load1")
        else:
            self.failUnlessEqual(pt.get_value(),"/dev/load1")

        if sys.platform == "win32":
            pt.set_dir("D:/foo")
        else:
            pt.set_dir("/dev/foo")
        pt.load("o1",["bar"])
        if sys.platform == "win32":
            self.failUnlessEqual(pt.get_value(),"d:\\foo\\bar")
        else:
            self.failUnlessEqual(pt.get_value(),"/dev/foo/bar")

        
    def test_OptionPlugin(self):
        """Test OptionPlugin"""
        ep = ExtensionPoint(IOption)
        class TMP(Plugin):
            declare_option("o1")
        obj = TMP()
        pt = ep.service("o1")

        try:
            pt.load("o1",[])
            self.fail("expected error")
        except OptionError:
            pass

        
if __name__ == "__main__":
   unittest.main()
