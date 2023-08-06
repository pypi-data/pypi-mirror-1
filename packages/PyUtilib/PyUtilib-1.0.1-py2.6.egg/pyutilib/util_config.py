#  _________________________________________________________________________
#
#  PyUtilib: A Python utility library.
#  Copyright (c) 2008 Sandia Corporation.
#  This software is distributed under the BSD License.
#  Under the terms of Contract DE-AC04-94AL85000 with Sandia Corporation,
#  the U.S. Government retains certain rights in this software.
#  For more information, see the PyUtilib README.txt file.
#  _________________________________________________________________________


import os
import sys
from optparse import OptionParser
import util_debug
import ConfigParser
from warnings import warn
from _exceptions import BadDebuggingValue

def _set_debugging_option(option, opt_str, value, parser):
    vals = value.split(",")
    for val in vals:
       tmp = val.strip()
       if not tmp in util_debug.Debug:
          raise BadDebuggingValue, tmp
       parser.values.debug.append( getattr(util_debug.Debug,tmp) )


class ConfigPlugin(object):
    """
    A class that adds options to a Config object
    """

    def __init__(self):
        """ Constructor
        """
        pass

    def add_options(self,parser):
        """ Add options to the parser
        """
        pass                            #pragma:nocover

    def configure(self, options, config):
        """ Configure the plugin with option info
        """
        pass                            #pragma:nocover

    def __repr__(self):
        """ Create string representation
        """
        d = self.__dict__.copy()
        keys = [ k for k in d.keys()
                  if not k.startswith('_') ]
        keys.sort()
        return "ConfigPlugin(%s)" % ', '.join([ '%s=%r' % (k, d[k])
                                          for k in keys ])

    __str__ = __repr__


class Config(object):
    """
    A configuration object for managing the processing of config
    files and related global data.

    Adapted from the design of the 'Config' class in the 'nose' 
    Python package.
    """

    def __init__(self, **kw):
        """Constructor
        """
        self._option_ignore = ['help']
        self._parser=None
        self._plugins=[]
        self.files = []
        self.debug = []
        self._sections = {}
        if os.name != 'nt':             #pragma nocover
           #
           # On unix use /tmp by default
           #
           self.tempdir = os.environ.get("TMPDIR", "/tmp")
        else:                           #pragma nocover
           #
           # On Windows use the current directory
           #
           self.tempdir = os.environ.get("TMPDIR", "C:\\tmp")
        self.tempdir = os.environ.get("TMP", self.tempdir)
        self.tempdir = os.environ.get("TEMP", self.tempdir)
        ##self.logStream = sys.stderr
        ##self.stream = sys.stderr
        #
        # Configure default and orig dictionaries
        #
        self._default = self.__dict__.copy()
        self.update(kw)
        self._orig = self.__dict__.copy()

    def write(self,fp=None):
        if fp is None:
           fp = sys.stdout
        #
        # WARNING: this method does not guarantee that
        # the written data can be re-read.
        # 
        # The problem is that the option names
        # may be different from the names used to store the data
        # when the options are parsed!
        #
        for section in self._sections:
            print >>fp, "["+section+"]"
            keys = self._sections[section]
            keys.sort()
            for key in keys:
                print >>fp, key+"="+str(getattr(self,key))
        
    def __repr__(self):
        """
        Create a string representation of this config instance
        """
        d = self.__dict__.copy()
        keys = [ k for k in d.keys()
                 if not k.startswith('_') ]
        keys.sort()
        tmp=""
        firstitem=True
        for k in keys:
          if not firstitem:
             tmp=tmp+", "
          if k != "debug":
             tmp = tmp + "%s=%r" % (k,d[k])
          else:
             tmp = tmp + "debug="
             tmp=tmp+"["
             first=True
             for item in d[k]:
               if not first:
                  tmp=tmp+","
               tmp=tmp+str(item)
               first=False
             tmp=tmp+"]"
          firstitem=False
        tmp = "Config(%s)" % tmp
        for plugin in self._plugins:
          tmp=tmp+"\n"+str(plugin)
        return tmp

    __str__ = __repr__

    def add_plugin(self, plugin):
        """Add a plugin"""
        self._plugins.append(plugin)

    def configure(self, files=None, argv=[], doc=None):
        """
        Parse argv arguments to initialize this class
        """
        parser = self._getParser(doc)
        #
        # Process files specified in the arguments
        #
        if not files is None:
           #print "HERE",files,argv
           argv = self._loadAll(files, argv)
        #
        # Process config files specified in this class
        #
        if not self.files is None:
           argv = self._loadAll(self.files, argv)
        #
        # Parse options
        #
        #print "HERE",argv
        options, args = parser.parse_args(argv)
        #
        # Load config files specified on the command line,
        # create a new argv set and reparse
        #
        if options.files:
            argv = self._loadAll(options.files, argv)
            options, args = parser.parse_args(argv)
        self._options=options
        #
        # Update configuration data with the final options
        #
        self.tempdir = options.tempdir
        self.debug = options.debug
        ##self.debugLog = options.debugLog
        ##self.loggingConfig = options.loggingConfig
        ##self.verbosity = options.verbosity
        ##self.configureLogging()
        #
        # Configure plugins
        #
        for plugin in self._plugins:
            plugin.configure(options, self)


    def _loadAll(self, files, argv):
        """
        Load an array of config files
        """
        if isinstance(files,basestring):
           argv = self.load(files,argv)
        else:
           for file in files:
             argv = self.load(file,argv)
        return argv

    def load(self, file, argv):
        """
        Load config from file (may be filename or file-like object)
        """
        cfg = ConfigParser.RawConfigParser()
        filedir=""
        try:
            try:
                cfg.readfp(file)
            except AttributeError:
                #
                # Filename not an fp
                #
                if not os.path.exists(file):
                   raise IOError, "File "+file+" does not exist"
                filedir=os.path.dirname(os.path.abspath(file))+os.sep
                cfg.read(file)
        except ConfigParser.Error, e:
            #
            # Error parsing configuration, so generate a warning and
            # return
            #
            warn("Error reading config file %s: %s" % (file, e),
                 RuntimeWarning)
            return argv     #pragma:nocover
        except IOError, e:
            #
            # Error opening configuration, so generate a warning and
            # return
            #
            warn("Error opening config file %s: %s" % (file, e),
                 RuntimeWarning)
            return argv     #pragma:nocover
        #
        # Process the configuration information
        #
        ##print "XX HERE",file,filedir
        file_argv = []
        for section in self._sections:
            ##print "X HERE",section
            if section not in cfg.sections():
                continue
            for optname in cfg.options(section):
                if optname in self._option_ignore:
                    continue
                if optname not in self._sections[section]:
                   warn("Error processing config file %s: unexpected option %s in section %s" % (file,optname,section), RuntimeWarning)
                   continue         #pragma:nocover
                value = cfg.get(section, optname)
                ##print "HERE",section,optname,value
                #
                # Try to guess the absolute path of a config file
                #
                if optname == "files":
                    value=filedir+value
                #print "X",optname,value
                file_argv.extend(self._cfgToArg(optname, value))
        #
        # Copy the given args and insert args loaded from file
        # between the program name (first arg) and the rest
        #
        combined = argv[:]
        return file_argv + combined

    def default(self):
        """
        Reset all config values to defaults.
        """
        self.__dict__.update(self._default)

    def reset(self):
        """
        Reset all config values to original values
        """
        self.__dict__ = self._orig
        self._orig = self.__dict__
        #self.__dict__.update(self._orig)

    def update(self,d):
        """
        Set the Config class dictionary
        """
        self.__dict__.update(d)

    def _getParser(self, doc=None):
        """
        Get the command line option parser.
        """
        #
        # If already generated, simply return it
        #
        if self._parser:
            return self._parser
        parser = OptionParser(doc)
        parser.add_option(
            "--files", 
            dest="files", action="append", 
            help="Load configuration from config file(s). May be specified "
                 "multiple times; in that case, all config files will be "
                 "loaded and combined")
        parser.add_option(
            "--tempdir", 
            dest="tempdir", action="store",
            default=self.tempdir,
            help="The directory for temporary files.")
        parser.add_option(
            "--debug", 
            dest="debug", action="callback",
            default=self.debug,
            callback=_set_debugging_option,
            type="string",
            help="Debugging level (default: none)")
        parser.set_defaults(debug=[])
        self._sections["globals"] = ["files","tempdir","debug"]
        if len(self._sections["globals"]) != (len(parser.option_list)-1):
           raise ValueError, "Config class misconfigured"   #pragma:nocover
        #
        # Iterate through plugins to get options
        #
        for plugin in self._plugins:
          prev = len(parser.option_list)-1
          section,names = plugin.add_options(parser)
          curr = len(parser.option_list)-1
          if len(names) != (curr-prev):
             raise ValueError, "Error processing plugin "+str(plugin)+" "+str(curr-prev)+" new options added, but "+str(len(names))+" options reported"
          if section in self._sections:
             self._sections[section] = self._sections[section]+names
          else:
             self._sections[section] = names
        #
        # Returns the parser
        #
        self._parser = parser
        return parser

    def _cfgToArg(self, optname, value):
        argv = []
        #
        # WARNING: this logic makes the strong assumption that if it 
        # looks like a boolean, then it must be a boolean.  A safer
        # mechanism would validate that the option is a boolean, but I
        # can't figure out how to get that info from the parser.
        #
        if self._flag(value):
            if self._bool(value):
                argv.append('--' + optname)
        else:
            argv.append('--' + optname)
            argv.append(value)
        return argv

    def _flag(self,val):
        """Does the value look like an on/off flag?"""
        val = str(val)
        if len(val) > 5:
            return False
        return val.upper() in ('F', 'T', 'TRUE', 'FALSE', 'ON', 'OFF')

    def _bool(self,val):
        return str(val).upper() in ('1', 'T', 'TRUE', 'ON')

