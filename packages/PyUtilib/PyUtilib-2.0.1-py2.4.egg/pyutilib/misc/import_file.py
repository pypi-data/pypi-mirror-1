#  _________________________________________________________________________
#
#  PyUtilib: A Python utility library.
#  Copyright (c) 2008 Sandia Corporation.
#  This software is distributed under the BSD License.
#  Under the terms of Contract DE-AC04-94AL85000 with Sandia Corporation,
#  the U.S. Government retains certain rights in this software.
#  For more information, see the PyUtilib README.txt file.
#  _________________________________________________________________________


import copy
import os
import imp 
import sys
import pyutilib
try:
    import runpy
    runpy_available=True
except ImportError:                             #pragma:nocover
    runpy_available=False

def import_file(filename, context=None):
    """
    Import a Python file as a module

    This function returns the module object that is created.
    """
    #if not runpy_available:                     #pragma:nocover
    	#raise pyutilib.ConfigurationError, "Cannot apply the import_file() function because runpy is not available"
    #
    # Parse the filename to get the name of the module to be imported
    #
    if '/' in filename:
       tmp_import = (filename).split("/")[-1]
    elif '\\' in filename:
       tmp_import = (filename).split("\\")[-1]
    else:
       tmp_import = filename
    name = ".".join((tmp_import).split(".")[:-1])
    #
    # Get the module if it already exists, and otherwise
    # import it
    #
    try:
        module = sys.modules[name]
    except KeyError:
        module = imp.load_source(name,filename)
    #
    # Add module to the give context
    #
    if not context is None:
       context[name] = module
    return module


def run_file(filename, logfile=None, execdir=None):
    """
    Execute a Python file and optionally redirect output to a logfile.
    """
    if not runpy_available:                     #pragma:nocover
    	raise pyutilib.ConfigurationError, "Cannot apply the run_file() function because runpy is not available"
    #
    # Open logfile
    #
    if not logfile is None:
       sys.stderr.flush()
       sys.stdout.flush()
       save_stdout = sys.stdout
       save_stderr = sys.stderr
       OUTPUT=open(logfile,"w")
       sys.stdout=OUTPUT
       sys.stderr=OUTPUT
    #
    # Add the file directory to the system path
    #
    if '/' in filename:
        tmp= "/".join((filename).split("/")[:-1])
        tmp_import = (filename).split("/")[-1]
        sys.path.append(tmp)
    elif '\\' in filename:
        tmp = "\\".join((filename).split("\\")[:-1])
        tmp_import = (filename).split("\\")[-1]
        sys.path.append(tmp)
    else:
        tmp_import = filename
    name = ".".join((tmp_import).split(".")[:-1])
    #
    # Run the module
    #
    try:
       if not execdir is None:
          tmp=os.getcwd()
          os.chdir(execdir)
       runpy.run_module(name,None,"__main__")
       if not execdir is None:
          os.chdir(tmp)
    except Exception, err:          #pragma:nocover
       if not logfile is None:
           OUTPUT.close()
           sys.stdout = save_stdout
           sys.stderr = save_stderr
       raise
    #
    # Close logfile
    #
    if not logfile is None:
        OUTPUT.close()
        sys.stdout = save_stdout
        sys.stderr = save_stderr
    
