#
# This example is taken from the description of the Trac component
# architecture.  
#

from trac.core import *
from trac.core import ComponentManager

class ITodoObserver(Interface):

        def todo_added(name, description):
            """Called when a to-do item is added."""

class TodoList(Component):
        observers = ExtensionPoint(ITodoObserver)

        def __init__(self):
            self.todos = {}

        def add(self, name, description):
            assert not name in self.todos, 'To-do already in list'
            self.todos[name] = description
            for observer in self.observers:
                observer.todo_added(name, description)

class TodoPrinter(Component):
        implements(ITodoObserver)

        def todo_added(self, name, description):
            print 'Task:', name
            print '     ', description

mngr = ComponentManager()
todo_list = TodoList(mngr)

todo_list.add('Make coffee', 'Really need to make some coffee')
todo_list.add('Bug triage', 'Double-check that all known issues were addressed')
