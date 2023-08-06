#  _________________________________________________________________________
#
#  PyUtilib: A Python utility library.
#  Copyright (c) 2008 Sandia Corporation.
#  This software is distributed under the BSD License.
#  Under the terms of Contract DE-AC04-94AL85000 with Sandia Corporation,
#  the U.S. Government retains certain rights in this software.
#  For more information, see the PyUtilib README.txt file.
#  _________________________________________________________________________

import os.path
import filecmp
import difflib

def remove_chars_in_list(s, l):
  if len(l) == 0:
    return s

  schars = []
  for c in s:
    if c not in l:
      schars.append(c)

  snew = "".join(schars)

  return snew


def get_desired_chars_from_file(f, nchars, l):
  retBuf = ""
  while nchars > 0:
    buf = f.read(nchars)
    if len(buf) == 0:
      break

    buf = remove_chars_in_list(buf, l)
    nchars -= len(buf)
    retBuf = retBuf + buf

  return retBuf


def file_diff(filename1,filename2):
    INPUT1=open(filename1,"r")
    lines1 = INPUT1.readlines()
    for i in range(0,len(lines1)):
        lines1[i] = lines1[i].strip()
    INPUT1.close()
    INPUT2=open(filename2,"r")
    lines2 = INPUT2.readlines()
    for i in range(0,len(lines2)):
        lines2[i] = lines2[i].strip()
    INPUT2.close()
    s=""
    for line in difflib.unified_diff(lines2,lines1,fromfile=filename2,tofile=filename1):
        s += line+"\n"
    return s


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
      return [False, None, ""]

    INPUT1=open(filename1,"r")
    INPUT2=open(filename2,"r")
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
           return [False, None, ""]

        if line1=="" or line2=="":
           return [True, lineno, file_diff(filename1,filename2)]

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
              return [True, lineno, file_diff(filename1,filename2)]
           if nc1 is None and nc2 is None:
              break
           index1=index1+1
           index2=index2+1


def compare_large_file(filename1,filename2, ignore=["\t"," ","\n","\r"]):
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

  bufSize = 1 * 1024 * 1024

  f1Size = os.stat(filename1).st_size
  f2Size = os.stat(filename2).st_size

  INPUT1=open(filename1,"r")
  INPUT2=open(filename2,"r")

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

