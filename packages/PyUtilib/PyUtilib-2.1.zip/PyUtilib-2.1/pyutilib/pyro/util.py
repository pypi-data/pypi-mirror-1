#  _________________________________________________________________________
#
#  PyUtilib: A Python utility library.
#  Copyright (c) 2008 Sandia Corporation.
#  This software is distributed under the BSD License.
#  Under the terms of Contract DE-AC04-94AL85000 with Sandia Corporation,
#  the U.S. Government retains certain rights in this software.
#  For more information, see the PyUtilib README.txt file.
#  _________________________________________________________________________

__all__ = ['get_nameserver']

import os
import Pyro.core
import Pyro.naming
from Pyro.errors import NamingError

def get_nameserver(host=None):
    if not host is None:
        os.environ['PYRO_NS_HOSTNAME'] = host
    elif 'PYRO_NS_HOSTNAME' in os.environ:
        host = os.environ['PYRO_NS_HOSTNAME']
    Pyro.core.initServer()
    try:
        if host is None:
            ns=Pyro.naming.NameServerLocator().getNS()
        else:
            ns=Pyro.naming.NameServerLocator().getNS(host)
    except NamingError, err:
        print "No nameserver found."
        if not host is None:
            print "  Cannot find nameserver host '%s'.  Error is '%s'." % (host,str(err))
        print "  Stopping."
        return None
    return ns

