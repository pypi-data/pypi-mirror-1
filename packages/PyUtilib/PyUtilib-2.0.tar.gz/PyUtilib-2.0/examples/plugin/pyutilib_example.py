#
# This example is adapted from the description of the Trac component
# architecture.  This illustrates how PyUtilib plugins are similar to
# Trac plugins.  The salient differences are:
#
#
# - The Component class is renamed to Plugin
#
# - The SingletonPlugin class is used to declare a singleton plugin that is
#   automatically registered.
#
# - The ComponentManager is renamed to ServiceManager
#
# - Plugin construction does not require a ServiceManager instance during
#   construction.
#

import os
import sys
from os.path import abspath, dirname
sys.path.insert(0, dirname(dirname(dirname(abspath(__file__)))))

from pyutilib.plugin import *


class ITodoObserver(Interface):

        def todo_added(name, description):
            """Called when a to-do item is added."""

class TodoList(Plugin):
        observers = ExtensionPoint(ITodoObserver)

        def __init__(self):
            self.todos = {}

        def add(self, name, description):
            assert not name in self.todos, 'To-do already in list'
            self.todos[name] = description
            for observer in self.observers:
                observer.todo_added(name, description)

class TodoPrinter(SingletonPlugin):
        implements(ITodoObserver)

        def todo_added(self, name, description):
            print 'Task:', name
            print '     ', description

todo_list = TodoList()

todo_list.add('Make coffee', 'Really need to make some coffee')
todo_list.add('Bug triage', 'Double-check that all known issues were addressed')
