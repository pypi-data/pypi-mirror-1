#  _________________________________________________________________________
#
#  PyUtilib: A Python utility library.
#  Copyright (c) 2008 Sandia Corporation.
#  This software is distributed under the BSD License.
#  Under the terms of Contract DE-AC04-94AL85000 with Sandia Corporation,
#  the U.S. Government retains certain rights in this software.
#  For more information, see the PyUtilib README.txt file.
#  _________________________________________________________________________

__all__ = ['Dispatcher', 'DispatcherServer']

import Pyro.core
import Pyro.naming
from Pyro.errors import NamingError
from Queue import Queue
from pyutilib.pyro.util import *

class Dispatcher(Pyro.core.ObjBase):

    def __init__(self):
        Pyro.core.ObjBase.__init__(self)
        self.default_taskqueue = Queue()
        self.default_resultqueue = Queue()
        self.taskqueue = {}
        self.resultqueue = {}

    def add_task(self, task, type=None):
        if type is None:
            self.default_taskqueue.put(task)
        else:
            if not type in self.taskqueue:
                self.taskqueue[type] = Queue()
            self.taskqueue[type].put(task)

    def get_task(self, type=None, timeout=5):
        if type is None:
            return self.default_taskqueue.get(block=True, timeout=timeout)
        else:
            try:
                self.taskqueue[type].get(block=True, timeout=timeout)
            except KeyError:
                return None

    def add_result(self, data, type=None):
        if type is None:
            self.default_resultqueue.put(data)
        else:
            if not type in self.resultqueue:
                self.resultqueue[type] = Queue()
            self.resultqueue[type].add(data)

    def get_result(self, type=None, timeout=5):
        if type is None:
            return self.default_resultqueue.get(block=True, timeout=timeout)
        else:
            try:
                self.taskqueue[type].get(block=True, timeout=timeout)
            except KeyError:
                return None

    def num_tasks(self, type=None):
        if type is None:
            return self.default_taskqueue.qsize()
        else:
            try:
                self.taskqueue[type].get(block=True, timeout=timeout)
            except KeyError:
                return 0

    def num_results(self, type=None):
        if type is None:
            return self.default_resultqueue.qsize()
        else:
            try:
                self.resultqueue[type].get(block=True, timeout=timeout)
            except KeyError:
                return 0
        

def DispatcherServer(group=":PyUtilibServer", host=None):
    #
    # main program
    #
    ns = get_nameserver(host)
    if ns is None:
        return
    daemon=Pyro.core.Daemon()
    daemon.useNameServer(ns)

    try:
        ns.createGroup(group)
    except NamingError:
        pass
    try:
        ns.unregister(group+".dispatcher")
    except NamingError:
        pass
    uri=daemon.connect(Dispatcher(),group+".dispatcher")
    
    print "Dispatcher is ready."
    daemon.requestLoop()

