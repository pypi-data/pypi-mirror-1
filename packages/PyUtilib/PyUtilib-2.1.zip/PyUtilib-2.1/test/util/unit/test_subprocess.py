#
# Unit Tests for util/math
#
#

import os
import sys
from os.path import abspath, dirname
sys.path.insert(0, dirname(dirname(abspath(__file__)))+"/../..")

import unittest
from nose.tools import nottest
from pyutilib import subprocess, SubprocessMngr, timer

class SubprocessDebug(unittest.TestCase):

    def test_foo(self):
        if not subprocess.mswindows:
           foo = SubprocessMngr("ls *py > /tmp/.pyutilib")
           foo.wait()
           print ""

           foo = SubprocessMngr("ls *py > /tmp/.pyutilib", stdout=subprocess.PIPE)
           foo.wait()
           for line in foo.process.stdout:
             print line,
           print ""
           os.remove("/tmp/.pyutilib")
        else:
           foo = SubprocessMngr("cmd /C \"dir\" > C:/tmp")
           foo.wait()
           print ""
     
        stime = timer()
        foo = SubprocessMngr("python -c \"while True: pass\"")
        foo.wait(10)
        print "Ran for " + `timer()-stime` + " seconds"

if __name__ == "__main__":
   unittest.main()
