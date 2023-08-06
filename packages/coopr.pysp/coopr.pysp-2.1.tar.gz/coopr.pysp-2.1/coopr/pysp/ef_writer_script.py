#  _________________________________________________________________________
#
#  Coopr: A COmmon Optimization Python Repository
#  Copyright (c) 2009 Sandia Corporation.
#  This software is distributed under the BSD License.
#  Under the terms of Contract DE-AC04-94AL85000 with Sandia Corporation,
#  the U.S. Government retains certain rights in this software.
#  For more information, see the Coopr README.txt file.
#  _________________________________________________________________________


import sys
import os
from optparse import OptionParser

import pyutilib.services
import textwrap
import traceback
import cProfile
import pstats
import gc

from coopr.pysp.ef import *

#
# Setup command-line options
#

parser = OptionParser()
parser.add_option("--model-directory",
                  help="The directory in which all model (reference and scenario) definitions are stored. Default is \".\".",
                  action="store",
                  dest="model_directory",
                  type="string",
                  default=".")
parser.add_option("--instance-directory",
                  help="The directory in which all instance (reference and scenario) definitions are stored. Default is \".\".",
                  action="store",
                  dest="instance_directory",
                  type="string",
                  default=".")
parser.add_option("--generate-weighted-cvar",
                  help="Add a weighted CVaR term to the primary objective",
                  action="store_true",
                  dest="generate_weighted_cvar",
                  default=False)
parser.add_option("--cvar-weight",
                  help="The weight associated with the CVaR term in the risk-weighted objective formulation.",
                  action="store",
                  dest="cvar_weight",
                  type="float",
                  default=1.0)
parser.add_option("--risk-alpha",
                  help="The probability threshold associated with cvar (or any future) risk-oriented performance metrics.",
                  action="store",
                  dest="risk_alpha",
                  type="float",
                  default=0.95)
parser.add_option("--output-file",
                  help="Specify the name of the extensive form output file",
                  action="store",
                  dest="output_file",
                  type="string",
                  default="efout.lp")
parser.add_option("--profile",
                  help="Enable profiling of Python code.  The value of this option is the number of functions that are summarized.",
                  action="store",
                  dest="profile",
                  default=0)
parser.usage="efwriter [options]"

def run_ef_writer(options, args):

   # if the user enabled the addition of the weighted cvar term to the objective,
   # then validate the associated parameters.
   generate_weighted_cvar = False
   cvar_weight = None
   risk_alpha = None

   if options.generate_weighted_cvar is True:

      generate_weighted_cvar = True
      cvar_weight = options.cvar_weight
      risk_alpha = options.risk_alpha

   write_ef_from_scratch(options.model_directory, options.instance_directory, options.output_file, \
                         generate_weighted_cvar, cvar_weight, risk_alpha)

   return

def run(args=None):

    #
    # Top-level command that executes the extensive form writer.
    # This is segregated from run_ef_writer to enable profiling.
    #

    # for a one-pass execution, garbage collection doesn't make
    # much sense - so I'm disabling it. Because: It drops the run-time
    # by a factor of 3-4 on bigger instances.
    gc.disable()       

    #
    # Parse command-line options.
    #
    try:
       (options, args) = parser.parse_args(args=args)
    except SystemExit:
       # the parser throws a system exit if "-h" is specified - catch
       # it to exit gracefully.
       return

    if options.profile > 0:
        #
        # Call the main ef writer with profiling.
        #
        tfile = pyutilib.services.TempfileManager.create_tempfile(suffix=".profile")
        tmp = cProfile.runctx('run_ef_writer(options,args)',globals(),locals(),tfile)
        p = pstats.Stats(tfile).strip_dirs()
        p.sort_stats('time', 'cum')
        options.profile = eval(options.profile)
        p = p.print_stats(options.profile)
        p.print_callers(options.profile)
        p.print_callees(options.profile)
        p = p.sort_stats('cum','calls')
        p.print_stats(options.profile)
        p.print_callers(options.profile)
        p.print_callees(options.profile)
        p = p.sort_stats('calls')
        p.print_stats(options.profile)
        p.print_callers(options.profile)
        p.print_callees(options.profile)
        pyutilib.services.TempfileManager.clear_tempfiles()
        ans = [tmp, None]
    else:
        #
        # Call the main EF writer without profiling.
        #
        ans = run_ef_writer(options, args)

    gc.enable()
    return ans

