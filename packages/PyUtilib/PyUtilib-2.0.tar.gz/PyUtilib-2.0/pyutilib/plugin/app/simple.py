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
This is a convenience class that configures the PyUtilib plugins framework
for a named application.  This class registers and activates a variety of
plugins that are commonly used in simple applications.
"""

import pyutilib
import os

class SimpleApplication(object):

    def __init__(self, name, filename=None):
        self.name = name
        if filename is None:
            self.filename = 'config.ini'
        else:
            self.filename = filename
        self.env = pyutilib.plugin.PluginEnvironment(name)
        pyutilib.plugin.PluginGlobals.push_env(self.env)
        self.config = pyutilib.plugin.Configuration(filename)
        self._env_config = pyutilib.plugin.EnvironmentConfig(name)
        self._env_config.options.path = os.getcwd()
        self.logger = pyutilib.plugin.LoggingConfig(name)
        self._egg_plugin = pyutilib.plugin.PluginFactory("EggLoader",namespace=name)

    def configure(self, filename):
        """Load a configuration file, and update options"""
        self.config.load(filename)

    def save_configuration(self, filename):
        """Save a configuration file"""
        self.config.save(filename)

    def exit(self):
        """Perform cleanup operations"""
        self.logger.shutdown()

    def log(self, message):
        """Generate logging output"""
        self.logger.log(message)

    def flush(self):
        """Flush the log output"""
        self.logger.flush()
