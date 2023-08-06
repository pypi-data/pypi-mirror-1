#
# Unit Tests for util/misc
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

class MiscDebug(unittest.TestCase):

    def test_tostr(self):
        """Verify that tostr() generates a string"""
        str = pyutilib.tostr([0.0,1])
        self.failUnlessEqual(str,"0.0 1")
        str = pyutilib.tostr([])
        self.failUnlessEqual(str,"")

    def test_flatten_tuple1(self):
        """Verify that flatten_tuple() flattens a normal tuple"""
        tmp=(1,"2",3.0)
        ans = pyutilib.flatten_tuple(tmp)
        self.failUnlessEqual(ans,tmp)

    def test_flatten_tuple2(self):
        """Verify that flatten_tuple() flattens a nested tuple"""
        tmp=(1,"2", (4,("5.0",(6)) ), 3.0)
        ans = pyutilib.flatten_tuple(tmp)
        target=(1,"2",4,"5.0",6,3.0)
        self.failUnlessEqual(ans,target)

    def test_flatten_tuple3(self):
        """Verify that flatten_tuple() returns a non-tuple"""
        tmp=[1,"2",3.0]
        ans = pyutilib.flatten_tuple(tmp)
        self.failUnlessEqual(ans,tmp)
    def test_Bunch(self):
        a=1
        b="b"
        tmp = pyutilib.Bunch(a=a, b=b)
        self.failUnlessEqual(tmp.a,a)
        self.failUnlessEqual(tmp.b,b)

    def test_flatten1(self):
        """Test that flatten works correctly"""
        self.failUnlessEqual([1,2,3], pyutilib.flatten((1,2,3)))
        self.failUnlessEqual([1,2,3,4], pyutilib.flatten((1,2,[3,4])))
        self.failUnlessEqual([1,2,'abc'], pyutilib.flatten((1,2,'abc')))
        self.failUnlessEqual([1,2,'abc'], pyutilib.flatten((1,2,('abc',))))
        a=set([0,9,8])
        self.failUnlessEqual([1,2,0,9,8], pyutilib.flatten((1,2,a)))

    def test_quote_split(self):
        ans=pyutilib.quote_split("[ ]+","a bb ccc")
        self.failUnlessEqual(ans,["a","bb","ccc"])
        ans=pyutilib.quote_split("[ ]+","")
        self.failUnlessEqual(ans,[])
        ans=pyutilib.quote_split("[ ]+",'a "bb ccc"')
        self.failUnlessEqual(ans,["a","\"bb ccc\""])
        try:
           ans=pyutilib.quote_split("[ ]+",'a "bb ccc')
           self.fail("test_quote_split - failed to detect unterminated quotation")
        except ValueError:
           pass

    def test_tuplize(self):
        ans=pyutilib.tuplize([0,1,2,3,4,5],2,"a")
        self.failUnlessEqual(ans,[(0,1),(2,3),(4,5)])
        try:
          ans=pyutilib.tuplize([0,1,2,3,4,5,6],2,"a")
          self.fail("test_tuplize failed to detect bad list length")
        except ValueError:
          pass

    def test_recursive_delete(self):
        if os.path.exists(".test_misc"):
           pyutilib.recursive_delete(".test_misc")
        os.makedirs(".test_misc/a/b/c")
        OUTPUT = open(".test_misc/a/file","w")
        print >>OUTPUT, "HERE"
        OUTPUT.close()
        pyutilib.recursive_delete(".test_misc")
        if os.path.exists(".test_misc"):
           self.fail("test_recursive_delete failed to delete .test_misc dir")

    def test_search_file(self):
        """ Test that search_file works """
        ans = pyutilib.search_file("foobar")
        self.failUnlessEqual(ans, None)
        path=sys.path+[currdir]
        ans = pyutilib.search_file("test1.cfg",search_path=path)
        self.failUnlessEqual(ans, abspath(currdir+"test1.cfg"))
        ans = pyutilib.search_file("test1", implicitExt=".cfg",search_path=path)
        self.failUnlessEqual(ans, abspath(currdir+"test1.cfg"))

    def test_search_file2(self):
        """ Test that search_file works with an empty PATH environment"""
        tmp = os.environ["PATH"]
        del os.environ["PATH"] 
        ans = pyutilib.search_file("cd")
        os.environ["PATH"] = tmp
        self.failUnlessEqual(ans, None)

    def test_file_compare1(self):
        """ Test that file comparison works """
        [flag,lineno] = pyutilib.compare_file(currdir+"filecmp1.txt",currdir+"filecmp1.txt")
        if flag:
           self.fail("test_file_compare1 - found differences in filecmp1.txt at line "+str(lineno))
        [flag,lineno] = pyutilib.compare_file(currdir+"filecmp1.txt",currdir+"filecmp2.txt")
        if flag:
           self.fail("test_file_compare1 - found differences between filecmp1.txt filecmp2.txt at line "+str(lineno))
        [flag,lineno] = pyutilib.compare_file(currdir+"filecmp1.txt",currdir+"filecmp3.txt")
        if not flag or lineno!=4:
           self.fail("test_file_compare1 - expected difference at line 4")
        [flag,lineno] = pyutilib.compare_file(currdir+"filecmp1.txt",currdir+"filecmp4.txt")
        if not flag or lineno!=3:
           self.fail("test_file_compare1 - expected difference at line 3")
        try:
           [flag,lineno] = pyutilib.compare_file(currdir+"foo.txt",currdir+"bar.txt")
           self.fail("test_file_compare1 - should have failed to find foo.txt")
        except IOError:
            pass
        try:
           [flag,lineno] = pyutilib.compare_file(currdir+"filecmp1.txt",currdir+"bar.txt")
           self.fail("test_file_compare1 - should have failed to find bar.txt")
        except IOError:
            pass

    def test_file_compare2(self):
        """ Test that large file comparison works """
        flag = pyutilib.compare_large_file(currdir+"filecmp1.txt",currdir+"filecmp1.txt")
        if flag:
           self.fail("test_file_compare2 - found differences in filecmp1.txt")
        flag = pyutilib.compare_large_file(currdir+"filecmp1.txt",currdir+"filecmp2.txt")
        if flag:
           self.fail("test_file_compare2 - found differences between filecmp1.txt filecmp2.txt")
        flag = pyutilib.compare_large_file(currdir+"filecmp2.txt",currdir+"filecmp3.txt",bufSize=7)
        if not flag:
           self.fail("test_file_compare2 - found differences between filecmp1.txt filecmp2.txt")
        flag = pyutilib.compare_large_file(currdir+"filecmp1.txt",currdir+"filecmp3.txt")
        if not flag:
           self.fail("test_file_compare2 - expected difference")
        flag = pyutilib.compare_large_file(currdir+"filecmp1.txt",currdir+"filecmp4.txt")
        if not flag:
           self.fail("test_file_compare2 - expected difference")
        try:
           flag = pyutilib.compare_large_file(currdir+"foo.txt",currdir+"bar.txt")
           self.fail("test_file_compare2 - should have failed to find foo.txt")
        except IOError:
            pass
        try:
           flag = pyutilib.compare_large_file(currdir+"filecmp1.txt",currdir+"bar.txt")
           self.fail("test_file_compare1 - should have failed to find bar.txt")
        except IOError:
            pass

    def test_argmax(self):
        """ Test that argmax works """
        a=[0,1,2,3]
        self.failUnlessEqual(a[pyutilib.argmax(a)],a[3])
        a=[3,2,1,0]
        self.failUnlessEqual(a[pyutilib.argmax(a)],a[0])
        
    def test_argmin(self):
        """ Test that argmin works """
        a=[0,1,2,3]
        self.failUnlessEqual(a[pyutilib.argmin(a)],a[0])
        a=[3,2,1,0]
        self.failUnlessEqual(a[pyutilib.argmin(a)],a[3])

    def test_remove_chars(self):
        """ Test the remove_chars_in_list works """
        a = pyutilib.remove_chars_in_list("","")
        self.failUnlessEqual(a,"")
        a = pyutilib.remove_chars_in_list("abcde","")
        self.failUnlessEqual(a,"abcde")
        a = pyutilib.remove_chars_in_list("abcde","ace")
        self.failUnlessEqual(a,"bd")
   
    def test_get_desired_chars_from_file(self):
        """ Test that get_desired_chars_from_file works """
        INPUT=open(currdir+"filecmp5.txt","r")
        a = pyutilib.get_desired_chars_from_file(INPUT,3,"b,d")
        self.failUnlessEqual(a,"ace")
        INPUT.close()
        INPUT=open(currdir+"filecmp5.txt","r")
        a = pyutilib.get_desired_chars_from_file(INPUT,100)
        self.failUnlessEqual(a,"abcde\nfghij\n")
        INPUT.close()

    def test_sort_index1(self):
        """Test that sort_index returns the correct value for a sorted array"""
        ans = pyutilib.sort_index( range(0,10) )
        self.failUnlessEqual(ans, range(0,10) )

    def test_sort_index2(self):
        """Test that sort_index returns an array that can be used to sort the data"""
        data = [4,2,6,8,1,9,3,10,7,5]
        ans = pyutilib.sort_index( data )
        sorted = []
        for i in range(0,len(data)):
            sorted.append( data[ans[i]] )
        data.sort()
        self.failUnlessEqual(data, sorted)
     
if __name__ == "__main__":
   unittest.main()
