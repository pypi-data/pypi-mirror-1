#  _________________________________________________________________________
#
#  Coopr: A COmmon Optimization Python Repository
#  Copyright (c) 2009 Sandia Corporation.
#  This software is distributed under the BSD License.
#  Under the terms of Contract DE-AC04-94AL85000 with Sandia Corporation,
#  the U.S. Government retains certain rights in this software.
#  For more information, see the Coopr README.txt file.
#  _________________________________________________________________________

from pyutilib.plugin.core import *
from coopr.pysp import phextension

class testphextension(SingletonPlugin):

    implements (phextension.IPHExtension)

    def post_ph_initialization(self, ph):
        """ Called after PH initialization!"""
        print "POST INITIALIZATION PH CALLBACK INVOKED"

    def post_iteration_0_solves(self, ph):
        """ Called after the iteration 0 solves!"""
        print "POST ITERATION 0 SOLVE PH CALLBACK INVOKED"        

    def post_iteration_0(self, ph):
        """ Called after the iteration 0 solves, averages computation, and weight computation"""
        print "POST ITERATION 0 PH CALLBACK INVOKED"                

    def post_iteration_k_solves(self, ph):
        """ Called after the iteration k solves!"""
        print "POST ITERATION K SOLVE PH CALLBACK INVOKED"                

    def post_iteration_k(self, ph):
        """ Called after the iteration k is finished!"""
        print "POST ITERATION K PH CALLBACK INVOKED"                        

    def post_ph_execution(self, ph):
        """ Called after PH has terminated!"""
        print "POST EXECUTION PH CALLBACK INVOKED"                        

    

