#  _________________________________________________________________________
#
#  PyUtilib: A Python utility library.
#  Copyright (c) 2008 Sandia Corporation.
#  This software is distributed under the BSD License.
#  Under the terms of Contract DE-AC04-94AL85000 with Sandia Corporation,
#  the U.S. Government retains certain rights in this software.
#  For more information, see the PyUtilib README.txt file.
#  _________________________________________________________________________

# This software is adapted from the Trac software (specifically, the trac.core
# module.  The Trac copyright statement is included below.

__all__ = ['EggLoader']

import os
from pyutilib.plugin import *
try:
    import pkg_resources
    from pkg_resources import working_set, DistributionNotFound, VersionConflict, UnknownExtra
    pkg_resources_avail=True
except ImportError:
    pkg_resources_avail=False


class EggLoader(ManagedPlugin):
    """
    Loader that looks for Python egg files in the plugins directories.
    These files get exampled with the pkg_resources package, and 
    Plugin classes are loaded.

    Note: this plugin should not be directly constructed.  Instead,
    the user should employ the PluginFactory_EggLoader function.
    """

    implements(IPluginLoader)

    def __init__(self, **kwds):
        """EggLoader constructor.  The 'namespace' keyword option is 
        required."""
        if 'name' not in kwds:
            kwds['name'] = "EggLoader."+kwds['namespace']
        super(EggLoader,self).__init__(**kwds)
        self.entry_point_name = kwds['namespace']+".plugins"
        PluginGlobals.env().log.warning('A dummy EggLoader service is being constructed, because the pkg_resources package is not available on this machine.')

    def load(self, env, search_path, disable_re, name_re):
        if not pkg_resources_avail:
            env.log.debug('The EggLoader service is terminating early because the pkg_resources package is not available on this machine.')
            return
            
        env.log.info('BEGIN -  Loading plugins with an EggLoader service')
        distributions, errors = working_set.find_plugins(
            pkg_resources.Environment(search_path)
        )
        for dist in distributions:
            if name_re.match(str(dist)):
                env.log.debug('Adding plugin %r from %r', dist, dist.location)
                working_set.add(dist)
            else:
                env.log.debug('Ignoring plugin %r from %r', dist, dist.location)

        def _log_error(item, e):
            if isinstance(e, DistributionNotFound):
                env.log.debug('Skipping "%s": ("%s" not found)', item, e)
            elif isinstance(e, VersionConflict):
                env.log.error('Skipping "%s": (version conflict "%s")',
                              item, e)
            elif isinstance(e, UnknownExtra):
                env.log.error('Skipping "%s": (unknown extra "%s")', item, e)
            elif isinstance(e, ImportError):
                env.log.error('Skipping "%s": (can\'t import "%s")', item, e)
            else:
                env.log.error('Skipping "%s": (error "%s")', item, e)

        for dist, e in errors.iteritems():
            _log_error(dist, e)

        for entry in working_set.iter_entry_points(self.entry_point_name):
            env.log.debug('Loading %r from %r', entry.name,
                          entry.dist.location)
            try:
                entry.load(require=True)
            except (ImportError, DistributionNotFound, VersionConflict,
                    UnknownExtra), e:
                _log_error(entry, e)
            else:
                #print "HERE",entry.dist.location, os.path.dirname(entry.dist.location)
                #print "HERE",entry.module_name,entry
                if not disable_re.match(os.path.dirname(entry.module_name)) is None:
                    #_enable_plugin(env, entry.module_name)
                    #print "HERE",entry.module_name,entry
                    pass

        env.log.info('END -    Loading plugins with an EggLoader service')


# Copyright (C) 2005-2008 Edgewall Software
# Copyright (C) 2005-2006 Christopher Lenz <cmlenz@gmx.de>
# All rights reserved.
#
# This software is licensed as described in the file COPYING, which
# you should have received as part of this distribution. The terms
# are also available at http://trac.edgewall.org/wiki/TracLicense.
#
# This software consists of voluntary contributions made by many
# individuals. For the exact contribution history, see the revision
# history and logs, available at http://trac.edgewall.org/log/.
#
# Author: Christopher Lenz <cmlenz@gmx.de>

