#  _________________________________________________________________________
#
#  PyUtilib: A Python utility library.
#  Copyright (c) 2008 Sandia Corporation.
#  This software is distributed under the BSD License.
#  Under the terms of Contract DE-AC04-94AL85000 with Sandia Corporation,
#  the U.S. Government retains certain rights in this software.
#  For more information, see the PyUtilib README.txt file.
#  _________________________________________________________________________

__all__ = ['TaskWorker', 'TaskWorkerServer']

import Pyro.core
import Queue
import os, socket
import pyutilib.pyro
from pyutilib.pyro.util import *
from Pyro.errors import NamingError

class TaskWorker(object):

    def __init__(self, group=":PyUtilibServer", type=None, host=None):
        self.type=type
        Pyro.core.initClient()
        self.ns = get_nameserver(host)
        if self.ns is None:
            return
        print 'Finding Pyro object...'
        try:
            URI=self.ns.resolve(group+".dispatcher")
            print 'URI:',URI
        except NamingError,x:
            print 'Couldn\'t find object, nameserver says:',x
            raise SystemExit
        self.dispatcher = Pyro.core.getProxyForURI(URI)
        self.WORKERNAME = "Worker_%d@%s" % (os.getpid(), socket.gethostname())
        print "This is worker",self.WORKERNAME
    
    def run(self):
        print "getting work from dispatcher."
    
        while 1:
            try:
                task = self.dispatcher.get_task(type=self.type)
            except Queue.Empty:
                pass
                #print "no work available yet."
            else:
                #
                # NOTE: should we return a task with an 
                # empty data element?  It isn't clear that we
                # need to send _back_ the data, but the factor
                # example takes advantage of the fact that it's sent
                # back...
                #
                task.result = self.process(task.data)
                task.processedBy = self.WORKERNAME
                self.dispatcher.add_result(task, type=self.type)


def TaskWorkerServer(cls, **kwds):
    host=None
    if 'argv' in kwds:
        argv = kwds['argv']
        if len(argv) == 2:
            host=argv[1]
        kwds['host'] = host
        del kwds['argv']
    worker = cls(**kwds)
    if worker.ns is None:
        return
    worker.run()
