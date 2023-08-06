#  _________________________________________________________________________
#
#  PyUtilib: A Python utility library.
#  Copyright (c) 2008 Sandia Corporation.
#  This software is distributed under the BSD License.
#  Under the terms of Contract DE-AC04-94AL85000 with Sandia Corporation,
#  the U.S. Government retains certain rights in this software.
#  For more information, see the PyUtilib README.txt file.
#  _________________________________________________________________________

"""PyUtilib: A utility library that includes a well-developed plugin framework. 

.. _Acro: https://software.sandia.gov/trac/acro
.. _Coopr: https://software.sandia.gov/trac/coopr
.. _FAST: https://software.sandia.gov/trac/fast
.. _`PyUtilib plugin framework`: https://software.sandia.gov/trac/pyutilib/wiki/Documentation/Plugins

PyUtilib has been developed to support several Python projects under development at Sandia National Laboratories, including Acro_, Coopr_ and FAST_.
PyUtilib includes utilities such as:

* A classes to manipulate Excel spreadsheets
* Utilities for using PLY parsers
* Utilies for generating cross-products of sets
* Functions to redirect IO
* A generic Factory utility
* Functions for standardizing floating point IO between 32-bit and 64-bit platforms
* A utility for conveniently importing modules
* Functions for performing an exact comparison of files
* Classes for singleton/unity objects

The `PyUtilib plugin framework`_ is the most developed element of PyUtilib. This
framework is derived from the Trac plugin framework, and it 
provides

* Support for both singleton and non-singleton plugin instances
* Utilities for managing plugins within namespaces
* A self-contained core that can be independently used from the PyUtilib plugins
* Commonly use plugins, including

  * A config-file reader/writer based on ConfigParser
  * Loading utilities for eggs and modules
  * A file manager for temporary files

"""

from __release__ import __version__, __date__

__maintainer__ = "William Hart"
__maintainer_email__ = "wehart@sandia.gov"
__copyright__ = "Copyright 2008 Sandia Corporation"
__license__ = "BSD"
__url__ = "https://software.sandia.gov/trac/pyutilib"

from _exceptions import *
from numtypes import *
from misc import *
from data import *
import plugin
from plugin_services import *
