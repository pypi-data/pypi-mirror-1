#  _________________________________________________________________________
#
#  PyUtilib: A Python utility library.
#  Copyright (c) 2008 Sandia Corporation.
#  This software is distributed under the BSD License.
#  Under the terms of Contract DE-AC04-94AL85000 with Sandia Corporation,
#  the U.S. Government retains certain rights in this software.
#  For more information, see the PyUtilib README.txt file.
#  _________________________________________________________________________

""" Utilities for using a global debugging value.

"""

from tpl.enum import Enum
from _exceptions import BadDebuggingValue
import util_globals

Debug = Enum('none', 'quiet', 'normal', 'verbose', 'all')


def debug(val=Debug.all, config=None):
    """
    Returns true if the debugging level equals val.

    By defualt, this looks at the global debugging level, but an optional
    configuration option can be passed.
    """
    if config is None:
       config = util_globals.config()
    if val not in Debug:
       raise BadDebuggingValue, str(val)
    if config.debug is True:
       return True
    if Debug.all in config.debug:
       return True
    if type(val) is str:
       tmp = getattr(Debug, val)
    else:
       tmp = val
    return tmp is not Debug.none and tmp in config.debug

def set_debugging(*args):
    """
    Sets the global debugging level.
    """
    config = util_globals.config()
    config.debug = []
    if args == ():
       args = ["all"]
    for val in args:
      if type(val) is str:
         if val not in Debug:
            raise BadDebuggingValue, val
         config.debug.append( getattr(Debug, val) )
      else:
         if val not in Debug:
            raise BadDebuggingValue, str(val)
         config.debug.append(val)

