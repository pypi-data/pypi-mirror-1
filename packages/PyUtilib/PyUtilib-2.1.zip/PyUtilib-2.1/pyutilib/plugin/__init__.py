#  _________________________________________________________________________
#
#  PyUtilib: A Python utility library.
#  Copyright (c) 2008 Sandia Corporation.
#  This software is distributed under the BSD License.
#  Under the terms of Contract DE-AC04-94AL85000 with Sandia Corporation,
#  the U.S. Government retains certain rights in this software.
#  For more information, see the PyUtilib README.txt file.
#  _________________________________________________________________________

"""
The outline of the PyUtilib plugin framework is adapted from Trac (see
the trac.core module).  This framework generalizes the Trac by supporting
multi-environment management of plugins, as well as non-singleton plugins.

This framework is organized as follows:

* core.py -  This is a stand-alone module that defines all of the core
aspects of the plugin framework.  All other components of the plugin
package can be viewed as extensions of this framework that support
current plugin-based applications.

* config - This sub-package includes utilities and plugins that support
configuration and logging.  In particular, this sub-package defines 
the ManagedPlugin class, which allows plugin services to be managed
through a configuration file.

* loader - This sub-package includes plugins for loading plugins.

* app - This sub-package includes simple applications that illustrate
the integration of all aspects of the plugin package.

* misc - Miscellaneous plugins.

NOTE: With the exception of the 'misc' sub-package, the plugin package
does not rely on any other part of PyUtilib.  Consequently, this package
can be independently used in other projects.
"""

from core import *

PluginGlobals.push_env("plugin")
from app import *
from config import *
from loader import *
from misc import *

#
# This declaration is here because this is a convenient place where
# all symbols in this module have been defined.
#

class IgnorePluginPlugins(SingletonPlugin):
    """Ignore plugins from the pyutilib.plugin module"""

    implements(IIgnorePluginWhenLoading)

    def ignore(self, name):
        return name in globals().keys()

#
# Remove the "plugin" environment as the default
#
PluginGlobals.pop_env()

