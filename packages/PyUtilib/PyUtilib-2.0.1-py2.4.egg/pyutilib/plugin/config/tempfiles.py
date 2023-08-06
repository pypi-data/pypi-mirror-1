#  _________________________________________________________________________
#
#  PyUtilib: A Python utility library.
#  Copyright (c) 2008 Sandia Corporation.
#  This software is distributed under the BSD License.
#  Under the terms of Contract DE-AC04-94AL85000 with Sandia Corporation,
#  the U.S. Government retains certain rights in this software.
#  For more information, see the PyUtilib README.txt file.
#  _________________________________________________________________________

"""A plugin that manages temporary files."""

__all__ = ['ITempfileManager', 'TempfileManagerPlugin', 'TempfileManager']

from options import *
from managed_plugin import *
import sys
import os
import tempfile


class ITempfileManager(Interface):
    """Interface for managing temporary files."""

    def create_tempname(self, filename):
        """Return the absolute path of a temporary filename that is guaranteed to be unique."""

    def add_tempfile(self, filename):
        """Declare this file to be temporary."""

    def clear_tempfiles(self):
        """Delete all temporary files."""


class TempfileManagerPlugin(ManagedSingletonPlugin):
    """A plugin that manages temporary files."""

    implements(ITempfileManager)

    def __init__(self, **kwds):
        kwds['name']='TempfileManager'
        ManagedSingletonPlugin.__init__(self,**kwds)
        self._tempfiles = []
        declare_option("tempdir", default=None)

    def create_tempfile(self, suffix=None, prefix=None, text=False, dir=None):
        """
        Return the absolute path of a temporary filename that is 
        guaranteed to be unique.  This function generates the file and returns
        the filename.
        """
        if suffix is None:
            suffix=''
        if prefix is None:
            prefix='tmp'
        if dir is None:
            dir=self.tempdir
        ans = tempfile.mkstemp(suffix=suffix, prefix=prefix, text=text, dir=dir)
        ans = list(ans)
        if not os.path.isabs(ans[1]):
            ans[1] = dir+os.sep+ans[1]
        self._tempfiles.append(ans[1])
        os.close(ans[0])
        os.remove(ans[1])
        return ans[1]

    def add_tempfile(self, filename):
        """Declare this file to be temporary."""
        tmp = os.path.abspath(fname)
        if not os.path.exists(tmp):
            raise IOError, "Temporary file does not exist: "+tmp
        self._tempfiles.append(tmp)


    def clear_tempfiles(self):
        """Delete all temporary files."""
        for file in self._tempfiles:
            if os.path.exists(file):
                os.remove(file)
        self._tempfiles=[]

#
# This global class provides a convenient handle to this
# singleton plugin
#
TempfileManager = TempfileManagerPlugin()
