#  _________________________________________________________________________
#
#  PyUtilib: A Python utility library.
#  Copyright (c) 2008 Sandia Corporation.
#  This software is distributed under the BSD License.
#  Under the terms of Contract DE-AC04-94AL85000 with Sandia Corporation,
#  the U.S. Government retains certain rights in this software.
#  For more information, see the PyUtilib README.txt file.
#  _________________________________________________________________________


import os
import filecmp
import unittest
import subprocess
from misc import *

#@nottest
def _run_cmd_baseline_test(self, cwd, cmd, outfile, baseline):
    if cwd is not None:
       oldpwd = os.getcwd()
       os.chdir(cwd)
    OUTPUT=open(outfile,"w")
    proc = subprocess.Popen(cmd.strip(),shell=True,stdout=OUTPUT,stderr=subprocess.STDOUT)
    proc.wait()
    OUTPUT.close()
    self.failUnlessFileEqualsBaseline(outfile, baseline)
    if cwd is not None:
       os.chdir(oldpwd)

#@nottest
def _run_fn_baseline_test(self, fn, name, baseline):
    (outfile, tmpfiles) = fn(name)
    self.failUnlessFileEqualsBaseline(outfile, baseline)
    for file in tmpfiles:
        os.remove(file)

#@nottest
def _run_fn_test(self, fn, name):
    explanation = fn(name)
    if explanation != "":
        self.fail(explanation)


class TestCase(unittest.TestCase):

    def __init__(self, methodName='runTest'):
        unittest.TestCase.__init__(self, methodName)

    def failUnlessFileEqualsBaseline(self,testfile,baseline):
        [flag,lineno,diffs] = compare_file(testfile,baseline)
        if not flag:
            os.remove(testfile)
        else:                                   #pragma:nocover
            self.fail("Unexpected output difference at line "+str(lineno) +":\n   testfile="+testfile+"\n   baseline="+baseline+"\nDiffs:\n"+diffs)
        return [flag,lineno]

    def failUnlessFileEqualsLargeBaseline(self,testfile,baseline):
        flag = compare_large_file(testfile,baseline)
        if not flag:
            os.remove(testfile)
        else:                                   #pragma:nocover
            self.fail("Unexpected output difference:\n   testfile="+testfile+"\n   baseline="+baseline)
        return flag

    def failUnlessFileEqualsBinaryFile(self,testfile,baseline):
        theSame = filecmp.cmp(testfile, baseline)
        if theSame:
            os.remove(testfile)
        else:                                   #pragma:nocover
            self.fail("Unexpected output difference:\n   testfile="+testfile+"\n   baseline="+baseline)
        return theSame

    def add_fn_test(name=None, fn=None):
        if fn is None:
            print "ERROR: must specify either the 'fn' option to define the test"
            return
        tmp = name.replace("/","_")
        tmp = tmp.replace("\\","_")
        tmp = tmp.replace(".","_")
        func = lambda self,c1=fn,c2=name: _run_fn_test(self,c1,c2)
        func.__name__ = "test_"+tmp
        setattr(TestCase, "test_"+tmp, func)
    add_fn_test=staticmethod(add_fn_test)
        
    def add_baseline_test(name=None, cmd=None, fn=None, baseline=None):
        if cmd is None and fn is None:
            print "ERROR: must specify either the 'cmd' or 'fn' option to define how the output file is generated"
            return
        if name is None and baseline is None:
            print "ERROR: must specify a baseline comparison file, or the test name"
            return
        if baseline is None:
            baseline=name+".txt"
        tmp = name.replace("/","_")
        tmp = tmp.replace("\\","_")
        tmp = tmp.replace(".","_")
        #
        # Create an explicit function so we can assign it a __name__ attribute.
        # This is needed by the 'nose' package
        #
        if fn is None:
            currdir=os.getcwd()
            func = lambda self,c1=currdir,c2=cmd,c3=tmp+".out",c4=baseline: _run_cmd_baseline_test(self,c1,c2,c3,c4)
        else:
            func = lambda self,c1=fn,c2=tmp,c3=baseline: _run_fn_baseline_test(self,c1,c2,c3)
        func.__name__ = "test_"+tmp
        setattr(TestCase, "test_"+tmp, func)
    add_baseline_test=staticmethod(add_baseline_test)


