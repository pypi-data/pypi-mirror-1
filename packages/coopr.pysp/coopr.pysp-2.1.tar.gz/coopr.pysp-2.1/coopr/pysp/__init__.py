#  _________________________________________________________________________
#
#  Coopr: A COmmon Optimization Python Repository
#  Copyright (c) 2008 Sandia Corporation.
#  This software is distributed under the BSD License.
#  Under the terms of Contract DE-AC04-94AL85000 with Sandia Corporation,
#  the U.S. Government retains certain rights in this software.
#  For more information, see the Coopr README.txt file.
#  _________________________________________________________________________

import pyutilib.plugin.core

pyutilib.plugin.core.PluginGlobals.push_env( "coopr.pysp" )

from scenariotree import *
from convergence import *
from ph import *
from phextension import *
from phutils import *
from ef import *
from ef_writer_script import *
from ph_script import *

pyutilib.plugin.core.PluginGlobals.pop_env()


try:
    import pkg_resources
    #
    # Load modules associated with Plugins that are defined in
    # EGG files.
    #
    for entrypoint in pkg_resources.iter_entry_points('coopr.pysp'):
        plugin_class = entrypoint.load()
except:
    pass

