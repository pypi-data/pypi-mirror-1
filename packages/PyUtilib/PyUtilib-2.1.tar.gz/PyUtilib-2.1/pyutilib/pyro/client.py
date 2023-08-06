#  _________________________________________________________________________
#
#  PyUtilib: A Python utility library.
#  Copyright (c) 2008 Sandia Corporation.
#  This software is distributed under the BSD License.
#  Under the terms of Contract DE-AC04-94AL85000 with Sandia Corporation,
#  the U.S. Government retains certain rights in this software.
#  For more information, see the PyUtilib README.txt file.
#  _________________________________________________________________________

__all__ = ['Client']

import Pyro.core
import Queue
import os, socket
from pyutilib.pyro.util import *
from Pyro.errors import NamingError

class Client(object):

    def __init__(self, group=":PyUtilibServer", type=None, host=None):
        self.type=type
        self.id = 0
        Pyro.core.initClient()
        self.ns = get_nameserver(host)
        if self.ns is None:
            return
        print 'Finding Pyro object...'
        try:
            self.URI=self.ns.resolve(group+".dispatcher")
            print 'URI:',self.URI
        except NamingError,x:
            print 'Couldn\'t find object, nameserver says:',x
            raise SystemExit
        self.set_group(group)
        self.CLIENTNAME = "Client_%d@%s:%%d" % (os.getpid(), socket.gethostname())
        print "This is client",self.CLIENTNAME

    def set_group(self, group):
        self.dispatcher = Pyro.core.getProxyForURI(self.URI)

    def add_task(self, task):
        if task.id is None:
            task.id = self.CLIENTNAME % (self.id)
            self.id += 1
        else:
            task.id = self.CLIENTNAME % (task.id)
        print "Adding task",task.id,"to queue",self.type
        self.dispatcher.add_task(task, type=self.type)

    def get_result(self):
        try:
            return self.dispatcher.get_result(type=self.type)
        except Queue.Empty:
            return None

    def num_tasks(self):
        return self.dispatcher.num_tasks(type=self.type)

    def num_results(self):
        return self.dispatcher.num_results(type=self.type)

