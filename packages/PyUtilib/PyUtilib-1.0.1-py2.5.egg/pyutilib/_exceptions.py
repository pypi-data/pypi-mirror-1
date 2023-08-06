#  _________________________________________________________________________
#
#  PyUtilib: A Python utility library.
#  Copyright (c) 2008 Sandia Corporation.
#  This software is distributed under the BSD License.
#  Under the terms of Contract DE-AC04-94AL85000 with Sandia Corporation,
#  the U.S. Government retains certain rights in this software.
#  For more information, see the PyUtilib README.txt file.
#  _________________________________________________________________________

class ConfigurationError(Exception):
    """
    An exception used there is an error configuring a package.
    """

    def __init__(self,*args,**kargs):
        Exception.__init__(self,*args,**kargs)      #pragma:nocover


class ApplicationError(Exception):
    """
    An exception used when an external application generates an error.
    """

    def __init__(self,*args,**kargs):
        Exception.__init__(self,*args,**kargs)      #pragma:nocover


class BadDebuggingValue(Exception):
    """
    An exception used when a bad debugging value is used.
    """

    def __init__(self,*args,**kargs):
        Exception.__init__(self,*args,**kargs)      #pragma:nocover

