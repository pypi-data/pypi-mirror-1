#  _________________________________________________________________________
#
#  PyUtilib: A Python utility library.
#  Copyright (c) 2008 Sandia Corporation.
#  This software is distributed under the BSD License.
#  Under the terms of Contract DE-AC04-94AL85000 with Sandia Corporation,
#  the U.S. Government retains certain rights in this software.
#  For more information, see the PyUtilib README.txt file.
#  _________________________________________________________________________

"""
Utilities for using a global configuration object
"""

import sys
import os
import os.path
import util_config

if (sys.platform[0:3] == "win"): #pragma:nocover
   executable_extension=".exe"
else:                            #pragma:nocover
   executable_extension=""


class _Globals:
    """
    A class that contains global data for pyutilib

    This class should not be used by end-users.
    """
    _config=None
    _tempfiles=[]


def config(_config=None):
    """
    A function for setting and getting the global configuration object.
    """
    if _config is None:
       if _Globals._config is None:
          _Globals._config = util_config.Config()
       return _Globals._config
    else:
       _Globals._config=_config
       return _Globals._config

def add_tempfile(fname):
    tmp = os.path.abspath(fname)
    if not os.path.exists(tmp):
       raise IOError, "Temporary file does not exist: "+tmp
    _Globals._tempfiles.append(tmp)
    
def remove_tempfiles():
    for file in _Globals._tempfiles:
      if not os.path.exists(file):
         raise IOError, "Cannot remove temporary file: "+file
      os.remove(file)
    _Globals._tempfiles=[]
