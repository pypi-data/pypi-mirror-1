#  _________________________________________________________________________
#
#  PyUtilib: A Python utility library.
#  Copyright (c) 2008 Sandia Corporation.
#  This software is distributed under the BSD License.
#  Under the terms of Contract DE-AC04-94AL85000 with Sandia Corporation,
#  the U.S. Government retains certain rights in this software.
#  For more information, see the PyUtilib README.txt file.
#  _________________________________________________________________________


import re
import string
import linecache
import sys
import os
import os.path
import filecmp
import string


if (sys.platform[0:3] == "win"): #pragma:nocover
   executable_extension=".exe"
else:                            #pragma:nocover
   executable_extension=""


def remove_chars_in_list(s, l):
  if len(l) == 0:
    return s

  schars = []
  for c in s:
    if c not in l:
      schars.append(c)

  snew = "".join(schars)

  return snew

def get_desired_chars_from_file(f, nchars, l=""):
  retBuf = ""
  while nchars > 0:
    buf = f.read(nchars)
    if len(buf) == 0:
      break

    buf = remove_chars_in_list(buf, l)
    nchars -= len(buf)
    retBuf = retBuf + buf

  return retBuf

def compare_file(filename1,filename2, ignore=["\t"," ","\n","\r"]):
    """
    Do a simple comparison of two files that ignores differences
    in newline types.
    
    The return value is the tuple: (status,lineno).  If status is True,
    then a difference has occured on the specified line number.  If 
    the status is False, then lineno is None.

    The goal of this utility is to simply indicate whether there are
    differences in files.  The Python 'difflib' is much more comprehensive
    and consequently more costly to apply.  The shutil.filecmp utility is
    similar, but it does not ignore differences in file newlines.  Also,
    this utility can ignore an arbitrary set of characters.
    """
    if not os.path.exists(filename1):
       raise IOError, "compare_file: cannot find file `"+filename1+"'"
    if not os.path.exists(filename2):
       raise IOError, "compare_file: cannot find file `"+filename2+"'"

    if filecmp.cmp(filename1, filename2):
      return [False, None]

    INPUT1=open(filename1)
    INPUT2=open(filename2)
    lineno=0
    while True:

        # If either line is composed entirely of characters to
        # ignore, then get another one.  In this way we can
        # skip blank lines that are in one file but not the other

        line1 = ""
        while len(line1) == 0:
          line1=INPUT1.readline()
          if line1 == "":
            break
          line1 = remove_chars_in_list(line1, ignore)
          lineno = lineno + 1

        line2 = ""
        while len(line2) == 0:
          line2=INPUT2.readline()
          if line2 == "":
            break
          line2 = remove_chars_in_list(line2, ignore)

        if line1=="" and line2=="":
           return [False,None]

        if line1=="" or line2=="":
           return [True,lineno]

        index1=0
        index2=0
        while True:
           # Set the value of nc1
           if index1 == len(line1):
              nc1=None
           else:
              nc1=line1[index1]
           # Set the value of nc2
           if index2 == len(line2):
              nc2=None
           else:
              nc2=line2[index2]
           # Compare curent character values
           if nc1 != nc2:
              return [True,lineno]
           if nc1 is None and nc2 is None:
              break
           index1=index1+1
           index2=index2+1


def compare_large_file(filename1,filename2, ignore=["\t"," ","\n","\r"], bufSize=1 * 1024 * 1024):
  """
  Do a simple comparison of two files that ignores white space, or
  characters specified in "ignore" list.
  
  The return value is True if a difference is found, False otherwise.

  For very long text files, this function will be faster than
  compare_file() because it reads the files in by large chunks
  instead of by line.  The cost is that you don't get the lineno
  at which the difference occurs.
  """

  result = False

  if not os.path.exists(filename1):
     raise IOError, "compare_large_file: cannot find file `"+filename1+"'"
  if not os.path.exists(filename2):
     raise IOError, "compare_large_file: cannot find file `"+filename2+"'"

  if filecmp.cmp(filename1, filename2):
    return result

  f1Size = os.stat(filename1).st_size
  f2Size = os.stat(filename2).st_size

  INPUT1=open(filename1)
  INPUT2=open(filename2)

  while True:
    buf1 = get_desired_chars_from_file(INPUT1, bufSize, ignore)
    buf2 = get_desired_chars_from_file(INPUT2, bufSize, ignore)

    if len(buf1) == 0 and len(buf2) == 0:
      break
    elif len(buf1) == 0 or len(buf2) == 0:
      result = True
      break

    if len(buf1) != len(buf2) or buf1 != buf2 :
      result = True
      break

  INPUT1.close()
  INPUT2.close()
  return result

def tostr(array):
  """ Create a string from an array of numbers """
  tmpstr = ""
  for val in array:
    tmpstr = tmpstr + " " + `val`
  return tmpstr.strip()


def flatten(x):
    """Flatten nested list"""
    result = []
    for el in x:
        if hasattr(el, "__iter__") and not isinstance(el, basestring):
            result.extend(flatten(el))
        else:
            result.append(el)
    return result

def flatten_tuple(val):
  """ Flatten nested tuples """
  if not isinstance(val,tuple):
     return val
  rv = ()
  for i in val:
    if isinstance(i,tuple):
       rv = rv + flatten_tuple(i)
    else:
       rv = rv + (i,)
  return rv


def recursive_delete(path,deleteRoot=True):
    """
    Recursively removes files and directories
    """
    if os.path.exists(path):
       for root, dirs, files in os.walk(path, topdown=False):
         for name in files:
           os.remove(os.path.join(root,name))
         for name in dirs:
           os.rmdir(os.path.join(root,name))
       if deleteRoot:
          os.rmdir(path)

class Bunch(dict):
    """
    A class that can be used to store a bunch of data dynamically
    
    foo = Bunch(data=y, sq=y*y, val=2)
    print foo.data
    print foo.sq
    print foo.val
    
    Adapted from code developed by Alex Martelli and submitted to
    the ActiveState Programmer Network http://aspn.activestate.com
    """
    def __init__(self, **kw):
        dict.__init__(self,kw)
        self.__dict__.update(kw)


def quote_split(re_str, str):
    """
    Split a string, but do not split the string between quotes.
    """
    mylist = []
    chars = []
    state = 1
    for token in re.split(re_str,str):
      prev = " "
      for character in token:
        if character == "\"" and prev != "\\":
           if state == 1:
              chars = chars + [ "\"" ]
              state = 2
           else:
              state = 1
              chars = chars + [ "\"" ]
        else:
           chars = chars + [ character ]
           prev = character
      if state == 1:
         if len(chars) > 0:
            mylist = mylist + [ string.join(chars,"") ]
            chars = []
      else:
         chars = chars + [ " " ]
    if state == 2:
       raise ValueError, "ERROR: unterminated quotation found in quote_split()"
    return mylist


def traceit(frame, event, arg):    #pragma:nocover
    """
    A utility for tracing Python executions.  Use this function by 
    executing:

    sys.settrace(traceit)
    """
    if event == "line":
        lineno = frame.f_lineno
        filename = frame.f_globals["__file__"]
        if (filename.endswith(".pyc") or
            filename.endswith(".pyo")):
            filename = filename[:-1]
        name = frame.f_globals["__name__"]
        line = linecache.getline(filename, lineno)
        print "%s:%s: %s" % (name, lineno, line.rstrip())
    return traceit


def tuplize(dlist, d, name):
    """
    Convert a list into a list of tuples.
    """
    if len(dlist) % d != 0:
       raise ValueError, "Cannot tuplize data for set "+str(name)+" because its length " + str(len(dlist)) + " is not a multiple of dimen " + str(d)
    j = 0
    t = []
    rv = []
    for i in dlist:
          t.append(i)
          j += 1
          if j == d:
                  rv.append(tuple(t))
                  t = []
                  j = 0
    return rv


def search_file(filename, search_path=None, implicitExt=executable_extension, executable=False, isfile=True):
    """
    Given a search path, find a file.

    Can specify the following options:
       path - A list of directories that are searched
       executable_extension - This string is used to see if there is an
           implicit extension in the filename
       executable - Test if the file is an executable (default=False)
       isfile - Test if the file is file (default=True)
    """
    if search_path is None:
        #
        # Use the PATH environment if it is defined and not empty
        #
        if "PATH" in os.environ and os.environ["PATH"] != "":
            search_path = string.split(os.environ["PATH"], os.pathsep)
        else:
            search_path = os.defpath.split(os.pathsep)
    for path in search_path:
      if os.path.exists(os.path.join(path, filename)) and \
         (not isfile or os.path.isfile(os.path.join(path, filename))):
         if not executable or os.access(os.path.join(path,filename),os.X_OK):
            return os.path.abspath(os.path.join(path, filename))
      if os.path.exists(os.path.join(path, filename+implicitExt)) and \
         (not isfile or os.path.isfile(os.path.join(path, filename+implicitExt))):
         if not executable or os.access(os.path.join(path,filename+implicitExt),os.X_OK):
            return os.path.abspath(os.path.join(path, filename+implicitExt))
    return None


def sort_index(l):
    """Returns a list, where the i-th value is the index of the i-th smallest
    value in the data 'l'"""
    return list(index for index, item in sorted(enumerate(l), key=lambda
item: item[1]))

