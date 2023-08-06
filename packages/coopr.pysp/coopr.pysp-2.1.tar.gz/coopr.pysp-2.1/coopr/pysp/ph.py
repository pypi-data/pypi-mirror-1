#  _________________________________________________________________________
#
#  Coopr: A COmmon Optimization Python Repository
#  Copyright (c) 2008 Sandia Corporation.
#  This software is distributed under the BSD License.
#  Under the terms of Contract DE-AC04-94AL85000 with Sandia Corporation,
#  the U.S. Government retains certain rights in this software.
#  For more information, see the Coopr README.txt file.
#  _________________________________________________________________________

import sys
import types
from coopr.pyomo import *
import copy
import os.path
import traceback
import copy
from coopr.opt import SolverResults,SolverStatus
from coopr.opt.base import SolverFactory
from coopr.opt.parallel import SolverManagerFactory
import time
import types
import pickle
from math import fabs, log, exp

from scenariotree import *
from phutils import *

from pyutilib.plugin.core import ExtensionPoint

from coopr.pysp.phextension import IPHExtension

class ProgressiveHedging(object):

   #
   # routine to compute linearization breakpoints uniformly between the bounds and the mean.
   #
   
   def compute_uniform_breakpoints(self, lb, node_min, xavg, node_max, ub, num_breakpoints_per_side):
      
      breakpoints = []

      # add the lower bound - the first breakpoint.
      breakpoints.append(lb)

      # determine the breakpoints to the left of the mean.
      left_step = (xavg - lb) / num_breakpoints_per_side
      current_x = lb
      for i in range(1,num_breakpoints_per_side+1):
         this_lb = current_x
         this_ub = current_x+left_step
         if (fabs(this_lb-lb) > self._integer_tolerance) and (fabs(this_lb-xavg) > self._integer_tolerance):
            breakpoints.append(this_lb)
         current_x += left_step            

      # add the mean - it's always a breakpoint. unless!
      # the lb or ub and the avg are the same.
      if (fabs(lb-xavg) > self._integer_tolerance) and (fabs(ub-xavg) > self._integer_tolerance):
         breakpoints.append(xavg)

      # determine the breakpoints to the right of the mean.
      right_step = (ub - xavg) / num_breakpoints_per_side
      current_x = xavg
      for i in range(1,num_breakpoints_per_side+1):
         this_lb = current_x
         this_ub = current_x+right_step
         if (fabs(this_ub-xavg) > self._integer_tolerance) and (fabs(this_ub-ub) > self._integer_tolerance):         
            breakpoints.append(this_ub)
         current_x += right_step

      # add the upper bound - the last breakpoint.
      # the upper bound should always be different than the lower bound (I say with some
      # hesitation - it really depends on what plugins are doing to modify the bounds dynamically).
      breakpoints.append(ub)

      return breakpoints

   #
   # routine to compute linearization breakpoints uniformly between the current node min/max bounds.
   #   

   def compute_uniform_between_nodestat_breakpoints(self, lb, node_min, xavg, node_max, ub, num_breakpoints):

      breakpoints = []

      # add the lower bound - the first breakpoint.
      breakpoints.append(lb)

      # add the node-min - the second breakpoint. but only if it is different than the lower bound and the mean.
      if (fabs(node_min-lb) > self._integer_tolerance) and (fabs(node_min-xavg) > self._integer_tolerance):      
         breakpoints.append(node_min)

      step = (node_max - node_min) / num_breakpoints
      current_x = node_min
      for i in range(1,num_breakpoints+1):
         this_lb = current_x
         this_ub = current_x+step
         if (fabs(this_lb-node_min) > self._integer_tolerance) and (fabs(this_lb-node_max) > self._integer_tolerance) and (fabs(this_lb-xavg) > self._integer_tolerance):
            breakpoints.append(this_lb)
         current_x += step            

      # add the node-max - the second-to-last breakpoint. but only if it is different than the upper bound and the mean.
      if (fabs(node_max-ub) > self._integer_tolerance) and (fabs(node_max-xavg) > self._integer_tolerance):            
         breakpoints.append(node_max)      

      # add the upper bound - the last breakpoint.
      breakpoints.append(ub)

      # add the mean - it's always a breakpoint. unless!
      # it happens to be equal to (within tolerance) the lower or upper bounds.
      # sort to insert it in the correct place.
      if (fabs(xavg - lb) > self._integer_tolerance) and (fabs(xavg - ub) > self._integer_tolerance):
         breakpoints.append(xavg)
      breakpoints.sort()

      return breakpoints

   #
   # routine to compute linearization breakpoints using "Woodruff" relaxation of the compute_uniform_between_nodestat_breakpoints.
   #   

   def compute_uniform_between_woodruff_breakpoints(self, lb, node_min, xavg, node_max, ub, num_breakpoints):

      breakpoints = []

      # add the lower bound - the first breakpoint.
      breakpoints.append(lb)

      # be either three "differences" from the mean, or else "halfway to the bound", whichever is closer to the mean.
      left = max(xavg - 3.0 * (xavg - node_min), xavg - 0.5 * (xavg - lb))
      right = min(xavg + 3.0 * (node_max - xavg), xavg + 0.5 * (ub - xavg))      

      # add the left bound - the second breakpoint. but only if it is different than the lower bound and the mean.
      if (fabs(left-lb) > self._integer_tolerance) and (fabs(left-xavg) > self._integer_tolerance):      
         breakpoints.append(left)

      step = (right - left) / num_breakpoints
      current_x = left
      for i in range(1,num_breakpoints+1):
         this_lb = current_x
         this_ub = current_x+step
         if (fabs(this_lb-left) > self._integer_tolerance) and (fabs(this_lb-right) > self._integer_tolerance) and (fabs(this_lb-xavg) > self._integer_tolerance):
            breakpoints.append(this_lb)
         current_x += step            

      # add the right bound - the second-to-last breakpoint. but only if it is different than the upper bound and the mean.
      if (fabs(right-ub) > self._integer_tolerance) and (fabs(right-xavg) > self._integer_tolerance):            
         breakpoints.append(right)      

      # add the upper bound - the last breakpoint.
      breakpoints.append(ub)

      # add the mean - it's always a breakpoint.
      # sort to insert it in the correct place.
      breakpoints.append(xavg)
      breakpoints.sort()

      return breakpoints

   #
   # routine to compute linearization breakpoints based on an exponential distribution from the mean in each direction.
   #   

   def compute_exponential_from_mean_breakpoints(self, lb, node_min, xavg, node_max, ub, num_breakpoints_per_side):

      breakpoints = []

      # add the lower bound - the first breakpoint.
      breakpoints.append(lb)

      # determine the breakpoints to the left of the mean.
      left_delta = xavg - lb
      base = exp(log(left_delta) / num_breakpoints_per_side)
      current_offset = base
      for i in range(1,num_breakpoints_per_side+1):
         current_x = xavg - current_offset
         if (fabs(current_x-lb) > self._integer_tolerance) and (fabs(current_x-xavg) > self._integer_tolerance):
            breakpoints.append(current_x)
         current_offset *= base

      # add the mean - it's always a breakpoint.
      breakpoints.append(xavg)

      # determine the breakpoints to the right of the mean.
      right_delta = ub - xavg
      base = exp(log(right_delta) / num_breakpoints_per_side)
      current_offset = base
      for i in range(1,num_breakpoints_per_side+1):
         current_x = xavg + current_offset
         if (fabs(current_x-xavg) > self._integer_tolerance) and (fabs(current_x-ub) > self._integer_tolerance):         
            breakpoints.append(current_x)
         current_offset *= base

      # add the upper bound - the last breakpoint.
      breakpoints.append(ub)         

      return breakpoints      

   #
   # a utility intended for folks who are brave enough to script rho setting in a python file.
   #

   def setRhoAllScenarios(self, variable_value, rho_expression):

      variable_name = None
      variable_index = None

      if isVariableNameIndexed(variable_value.name) is True:

         variable_name, variable_index = extractVariableNameAndIndex(variable_value.name)

      else:

         variable_name = variable_value.name
         variable_index = None
      
      new_rho_value = rho_expression()

      if self._verbose is True:
         print "Setting rho="+str(new_rho_value)+" for variable="+variable_value.name

      for instance_name, instance in self._instances.items():

         rho_param = getattr(instance, "PHRHO_"+variable_name)
         rho_param[variable_index] = new_rho_value

   #
   # a utility intended for folks who are brave enough to script variable bounds setting in a python file.
   #

   def setVariableBoundsAllScenarios(self, variable_name, variable_index, lower_bound, upper_bound):

      if isinstance(lower_bound, float) is False:
         raise ValueError, "Lower bound supplied to PH method setVariableBoundsAllScenarios for variable="+variable_name+indexToString(variable_index)+" must be a constant; value supplied="+str(lower_bound)

      if isinstance(upper_bound, float) is False:
         raise ValueError, "Upper bound supplied to PH method setVariableBoundsAllScenarios for variable="+variable_name+indexToString(variable_index)+" must be a constant; value supplied="+str(upper_bound)

      for instance_name, instance in self._instances.items():

         variable = getattr(instance, variable_name)
         variable[variable_index].setlb(lower_bound)
         variable[variable_index].setub(upper_bound)

   #
   # a utility intended for folks who are brave enough to script variable bounds setting in a python file.
   # same functionality as above, but applied to all indicies of the variable, in all scenarios.
   #

   def setVariableBoundsAllIndicesAllScenarios(self, variable_name, lower_bound, upper_bound):

      if isinstance(lower_bound, float) is False:
         raise ValueError, "Lower bound supplied to PH method setVariableBoundsAllIndiciesAllScenarios for variable="+variable_name+" must be a constant; value supplied="+str(lower_bound)

      if isinstance(upper_bound, float) is False:
         raise ValueError, "Upper bound supplied to PH method setVariableBoundsAllIndicesAllScenarios for variable="+variable_name+" must be a constant; value supplied="+str(upper_bound)

      for instance_name, instance in self._instances.items():

         variable = getattr(instance, variable_name)
         for index in variable:
            variable[index].setlb(lower_bound)
            variable[index].setub(upper_bound)

   #
   # checkpoint the current PH state via pickle'ing. the input iteration count
   # simply serves as a tag to create the output file name. everything with the
   # exception of the _ph_plugins, _solver_manager, and _solver attributes are
   # pickled. currently, plugins fail in the pickle process, which is fine as
   # JPW doesn't think you want to pickle plugins (particularly the solver and
   # solver manager) anyway. For example, you might want to change those later,
   # after restoration - and the PH state is independent of how scenario
   # sub-problems are solved.
   #

   def checkpoint(self, iteration_count):

      checkpoint_filename = "checkpoint."+str(iteration_count)

      tmp_ph_plugins = self._ph_plugins
      tmp_solver_manager = self._solver_manager
      tmp_solver = self._solver

      self._ph_plugins = None
      self._solver_manager = None
      self._solver = None
      
      checkpoint_file = open(checkpoint_filename, "w")
      pickle.dump(self,checkpoint_file)
      checkpoint_file.close()

      self._ph_plugins = tmp_ph_plugins
      self._solver_manager = tmp_solver_manager
      self._solver = tmp_solver

      print "Checkpoint written to file="+checkpoint_filename
   
   #
   # a simple utility to count the number of continuous and discrete variables in a set of instances.
   # unused variables are ignored, and counts include all active indices. returns a pair - num-discrete,
   # num-continuous.
   #

   def compute_variable_counts(self):

      num_continuous_vars = 0
      num_discrete_vars = 0
      
      for stage in self._scenario_tree._stages[:-1]: # no blending over the final stage

         for tree_node in stage._tree_nodes:

            for (variable, index_template, variable_indices) in stage._variables:

               for index in variable_indices:

                  is_used = True # until proven otherwise                     
                  for scenario in tree_node._scenarios:
                     instance = self._instances[scenario._name]
                     if getattr(instance,variable.name)[index].status == VarStatus.unused:
                        is_used = False

                  if is_used is True:                        

                     if isinstance(variable.domain, IntegerSet) or isinstance(variable.domain, BooleanSet):
                        num_discrete_vars = num_discrete_vars + 1
                     else:
                        num_continuous_vars = num_continuous_vars + 1

      return (num_discrete_vars, num_continuous_vars)

   #
   # ditto above, but count the number of fixed discrete and continuous variables.
   # important: once a variable (value) is fixed, it is flagged as unused in the
   # course of presolve - because it is no longer referenced. this makes sense,
   # of course; it's just something to watch for. this is an obvious assumption
   # that we won't be fixing unused variables, which should not be an issue.
   #

   def compute_fixed_variable_counts(self):

      num_fixed_continuous_vars = 0
      num_fixed_discrete_vars = 0
      
      for stage in self._scenario_tree._stages[:-1]: # no blending over the final stage
         
         for tree_node in stage._tree_nodes:

            for (variable, index_template, variable_indices) in stage._variables:

               for index in variable_indices:

                  # implicit assumption is that if a variable value is fixed in one
                  # scenario, it is fixed in all scenarios. 

                  is_fixed = False # until proven otherwise
                  for scenario in tree_node._scenarios:
                     instance = self._instances[scenario._name]
                     var_value = getattr(instance,variable.name)[index]
                     if var_value.fixed is True:
                        is_fixed = True

                  if is_fixed is True:

                     if isinstance(variable.domain, IntegerSet) or isinstance(variable.domain, BooleanSet):
                        num_fixed_discrete_vars = num_fixed_discrete_vars + 1
                     else:
                        num_fixed_continuous_vars = num_fixed_continuous_vars + 1                           

      return (num_fixed_discrete_vars, num_fixed_continuous_vars)

   # a utility to create piece-wise linear constraint expressions for a given variable, for
   # use in constructing the augmented (penalized) PH objective. lb and ub are the bounds
   # on this piece, variable is the actual instance variable, and average is the instance
   # parameter specifying the average of this variable across instances sharing passing
   # through a common tree node. lb and ub are floats. 
   def _create_piecewise_constraint_expression(self, lb, ub, instance_variable, variable_average, quad_variable):

      penalty_at_lb = (lb - variable_average()) * (lb - variable_average())
      penalty_at_ub = (ub - variable_average()) * (ub - variable_average())
      slope = (penalty_at_ub - penalty_at_lb) / (ub - lb)
      intercept = penalty_at_lb - slope * lb
      expression = (0.0, quad_variable - slope * instance_variable - intercept, None)

      return expression

   # when the quadratic penalty terms are approximated via piecewise linear segments,
   # we end up (necessarily) "littering" the scenario instances with extra constraints.
   # these need to and should be cleaned up after PH, for purposes of post-PH manipulation,
   # e.g., writing the extensive form. 
   def _cleanup_scenario_instances(self):

      for instance_name, instance in self._instances.items():

         for constraint_name in self._instance_augmented_attributes[instance_name]:

            instance._clear_attribute(constraint_name)

         # if you don't pre-solve, the name collections won't be updated.
         instance.presolve()

   # create PH weight and xbar vectors, on a per-scenario basis, for each variable that is not in the 
   # final stage, i.e., for all variables that are being blended by PH. the parameters are created
   # in the space of each scenario instance, so that they can be directly and automatically
   # incorporated into the (appropriately modified) objective function.

   def _create_ph_scenario_parameters(self):

      for (instance_name, instance) in self._instances.items():

         # first, gather all unique variables referenced in any stage
         # other than the last, independent of specific indices. this
         # "gather" step is currently required because we're being lazy
         # in terms of index management in the scenario tree - which
         # should really be done in terms of sets of indices.
         # NOTE: technically, the "instance variables" aren't really references
         # to the variable in the instance - instead, the reference model. this
         # isn't an issue now, but it could easily become one (esp. in avoiding deep copies).
         instance_variables = {}
         
         for stage in self._scenario_tree._stages[:-1]:
            
            for (reference_variable, index_template, reference_indices) in stage._variables:
                  
               if reference_variable.name not in instance_variables.keys():
                     
                  instance_variables[reference_variable.name] = reference_variable

         # for each blended variable, create a corresponding ph weight and average parameter in the instance.
         # this is a bit wasteful, in terms of indices that might appear in the last stage, but that is minor
         # in the grand scheme of things.

         for (variable_name, reference_variable) in instance_variables.items():

            # PH WEIGHT

            new_w_index = reference_variable._index
            new_w_parameter_name = "PHWEIGHT_"+reference_variable.name
            new_w_parameter = Param(new_w_index,name=new_w_parameter_name)
            setattr(instance,new_w_parameter_name,new_w_parameter)

            # if you don't explicitly assign values to each index, the entry isn't created - instead, when you reference
            # the parameter that hasn't been explicitly assigned, you just get the default value as a constant. I'm not
            # sure if this has to do with the model output, or the function of the model, but I'm doing this to avoid the
            # issue in any case for now.
            for index in new_w_index:
               new_w_parameter[index] = 0.0

            # PH AVG

            new_avg_index = reference_variable._index 
            new_avg_parameter_name = "PHAVG_"+reference_variable.name
            new_avg_parameter = Param(new_avg_index,name=new_avg_parameter_name)
            setattr(instance,new_avg_parameter_name,new_avg_parameter)

            for index in new_avg_index:
               new_avg_parameter[index] = 0.0

            # PH RHO

            new_rho_index = reference_variable._index 
            new_rho_parameter_name = "PHRHO_"+reference_variable.name
            new_rho_parameter = Param(new_rho_index,name=new_rho_parameter_name)
            setattr(instance,new_rho_parameter_name,new_rho_parameter)

            for index in new_rho_index:
               new_rho_parameter[index] = self._rho

            # PH LINEARIZED PENALTY TERM

            if self._linearize_nonbinary_penalty_terms > 0:

               new_penalty_term_variable_index = reference_variable._index
               new_penalty_term_variable_name = "PHQUADPENALTY_"+reference_variable.name
               # this is a quadratic penalty term - the lower bound is 0!
               new_penalty_term_variable = Var(new_penalty_term_variable_index, name=new_penalty_term_variable_name, bounds=(0.0,None))
               new_penalty_term_variable.construct()
               setattr(instance, new_penalty_term_variable_name, new_penalty_term_variable)
               self._instance_augmented_attributes[instance_name].append(new_penalty_term_variable_name)

            # BINARY INDICATOR PARAMETER FOR WHETHER SPECIFIC VARIABLES ARE BLENDED. FOR ADVANCED USERS ONLY. 

            # also controls whether weight updates proceed at any iteration.

            new_blend_index = reference_variable._index
            new_blend_parameter_name = "PHBLEND_"+reference_variable.name
            new_blend_parameter = Param(new_blend_index, name=new_blend_parameter_name, within=Binary)
            setattr(instance,new_blend_parameter_name,new_blend_parameter)

            for index in new_blend_index:
               new_blend_parameter[index] = 1
      

   """ Constructor
       Arguments:
          max_iterations        the maximum number of iterations to run PH (>= 0). defaults to 0.
          rho                   the global rho value (> 0). defaults to 0.
          rho_setter            an optional name of a python file used to set particular variable rho values.
          solver                the solver type that PH uses to solve scenario sub-problems. defaults to "cplex".
          solver_manager        the solver manager type that coordinates scenario sub-problem solves. defaults to "serial".
          keep_solver_files     do I keep intermediate solver files around (for debugging)? defaults to False.
          output_solver_log     do I dump the solver log (as it is being generated) to the screen? defaults to False.
          output_solver_results do I output (for debugging) the detailed solver results, including solutions, for scenario solves? defaults to False.
          verbose               does the PH object stream debug/status output? defaults to False.
          output_times          do I output timing statistics? defaults to False (e.g., useful in the case where you want to regression test against baseline output).
          checkpoint_interval   how many iterations between writing a checkpoint file containing the entire PH state? defaults to 0, indicating never.

   """
   def __init__(self, *args, **kwds):

      # PH configuration parameters
      self._rho = 0.0 # a default, global values for rhos.
      self._rho_setter = None # filename for the modeler to set rho on a per-variable or per-scenario basis.
      self._bounds_setter = None # filename for the modeler to set rho on a per-variable basis, after all scenarios are available.
      self._max_iterations = 0

      # PH reporting parameters
      self._verbose = False # do I flood the screen with status output?
      self._output_continuous_variable_stats = True # when in verbose mode, do I output weights/averages for continuous variables?
      self._output_solver_results = False
      self._output_times = False

      # PH run-time variables
      self._current_iteration = 0 # the 'k'
      self._xbar = {} # current per-variable averages. maps (node_id, variable_name) -> value
      self._initialized = False # am I ready to call "solve"? Set to True by the initialize() method.

      # PH solver information / objects.
      self._solver_type = "cplex"
      self._solver_manager_type = "serial" # serial or pyro are the options currently available
      
      self._solver = None # will eventually be unnecessary once Bill eliminates the need for a solver in the solver manager constructor.
      self._solver_manager = None 
      
      self._keep_solver_files = False
      self._output_solver_log = False

      # PH convergence computer/updater.
      self._converger = None

      # PH history
      self._solutions = {}

      # the checkpoint interval - expensive operation, but worth it for big models.
      # 0 indicates don't checkpoint.
      self._checkpoint_interval = 0

      # all information related to the scenario tree (implicit and explicit).
      self._model = None # not instantiated
      self._model_instance = None # instantiated

      self._scenario_tree = None
      
      self._scenario_data_directory = "" # this the prefix for all scenario data
      self._instances = {} # maps scenario name to the corresponding model instance
      self._instance_augmented_attributes = {} # maps scenario name to a list of the constraints added (e.g., for piecewise linear approximation) to the instance by PH.

      # for various reasons (mainly hacks at this point), it's good to know whether we're minimizing or maximizing.
      self._is_minimizing = None

      # global handle to ph extension plugins
      self._ph_plugins = ExtensionPoint(IPHExtension)

      # PH timing statistics - relative to last invocation.
      self._init_start_time = None # for initialization() method
      self._init_end_time = None
      self._solve_start_time = None # for solve() method
      self._solve_end_time = None
      self._cumulative_solve_time = None # seconds, over course of solve()
      self._cumulative_xbar_time = None # seconds, over course of update_xbars()
      self._cumulative_weight_time = None # seconds, over course of update_weights()

      # do I disable warm-start for scenario sub-problem solves during PH iterations >= 1?
      self._disable_warmstarts = False

      # do I drop proximal (quadratic penalty) terms from the weighted objective functions?
      self._drop_proximal_terms = False

      # do I linearize the quadratic penalty term for continuous variables via a
      # piecewise linear approximation? the default should always be 0 (off), as the
      # user should be aware when they are forcing an approximation.
      self._linearize_nonbinary_penalty_terms = 0

      # the breakpoint distribution strategy employed when linearizing. 0 implies uniform
      # distribution between the variable lower and upper bounds.
      self._breakpoint_strategy = 0

      # do I retain quadratic objective terms associated with binary variables? in general,
      # there is no good reason to not linearize, but just in case, I introduced the option.
      self._retain_quadratic_binary_terms = False

      # PH default tolerances - for use in fixing and testing equality across scenarios,
      # and other stuff.
      self._integer_tolerance = 0.00001

      # PH maintains a mipgap that is applied to each scenario solve that is performed.
      # this attribute can be changed by PH extensions, and the change will be applied
      # on all subsequent solves - until it is modified again. the default is None,
      # indicating unassigned.
      self._mipgap = None

      # we only store these temporarily...
      scenario_solver_options = None

      # process the keyword options
      for key in kwds.keys():
         if key == "max_iterations":
            self._max_iterations = kwds[key]
         elif key == "rho":
            self._rho = kwds[key]
         elif key == "rho_setter":
            self._rho_setter = kwds[key]
         elif key == "bounds_setter":
            self._bounds_setter = kwds[key]                        
         elif key == "solver":
            self._solver_type = kwds[key]
         elif key == "solver_manager":
            self._solver_manager_type = kwds[key]
         elif key == "scenario_solver_options":
            scenario_solver_options = kwds[key]
         elif key == "scenario_mipgap":
            self._mipgap = kwds[key]            
         elif key == "keep_solver_files":
            self._keep_solver_files = kwds[key]
         elif key == "output_solver_results":
            self._output_solver_results = kwds[key]
         elif key == "output_solver_log":
            self._output_solver_log = kwds[key]
         elif key == "verbose":
            self._verbose = kwds[key]
         elif key == "output_times":
            self._output_times = kwds[key]
         elif key == "disable_warmstarts":
            self._disable_warmstarts = kwds[key]
         elif key == "drop_proximal_terms":
            self._drop_proximal_terms = kwds[key]
         elif key == "retain_quadratic_binary_terms":
            self._retain_quadratic_binary_terms = kwds[key]
         elif key == "linearize_nonbinary_penalty_terms":
            self._linearize_nonbinary_penalty_terms = kwds[key]
         elif key == "breakpoint_strategy":
            self._breakpoint_strategy = kwds[key]
         elif key == "checkpoint_interval":
            self._checkpoint_interval = kwds[key]            
         else:
            print "Unknown option=" + key + " specified in call to PH constructor"

      # validate all "atomic" options (those that can be validated independently)
      if self._max_iterations < 0:
         raise ValueError, "Maximum number of PH iterations must be non-negative; value specified=" + `self._max_iterations`
      if self._rho <= 0.0:
         raise ValueError, "Value of the rho parameter in PH must be non-zero positive; value specified=" + `self._rho`
      if (self._mipgap is not None) and ((self._mipgap < 0.0) or (self._mipgap > 1.0)):
         raise ValueError, "Value of the mipgap parameter in PH must be on the unit interval; value specified=" + `self._mipgap`

      # validate the linearization (number of pieces) and breakpoint distribution parameters.
      if self._linearize_nonbinary_penalty_terms < 0:
         raise ValueError, "Value of linearization parameter for nonbinary penalty terms must be non-negative; value specified=" + `self._linearize_nonbinary_penalty_terms`         
      if self._breakpoint_strategy < 0:
         raise ValueError, "Value of the breakpoint distribution strategy parameter must be non-negative; value specified=" + str(self._breakpoint_strategy)
      if self._breakpoint_strategy > 3:
         raise ValueError, "Unknown breakpoint distribution strategy specified - valid values are between 0 and 2, inclusive; value specified=" + str(self._breakpoint_strategy)
   
      # validate rho setter file if specified.
      if self._rho_setter is not None:
         if os.path.exists(self._rho_setter) is False:
            raise ValueError, "The rho setter script file="+self._rho_setter+" does not exist"

      # validate bounds setter file if specified.
      if self._bounds_setter is not None:
         if os.path.exists(self._bounds_setter) is False:
            raise ValueError, "The bounds setter script file="+self._bounds_setter+" does not exist"      

      # validate the checkpoint interval.
      if self._checkpoint_interval < 0:
         raise ValueError, "A negative checkpoint interval with value="+str(self._checkpoint_interval)+" was specified in call to PH constructor"

      # construct the sub-problem solver.
      if self._verbose is True:
         print "Constructing solver type="+self._solver_type         
      self._solver = SolverFactory(self._solver_type)
      if self._solver == None:
         raise ValueError, "Unknown solver type=" + self._solver_type + " specified in call to PH constructor"
      if self._keep_solver_files is True:
         self._solver.keepFiles = True
      if len(scenario_solver_options) > 0:
         if self._verbose is True:
            print "Initializing scenario sub-problem solver with options="+str(scenario_solver_options)
         self._solver.set_options("".join(scenario_solver_options))

      # construct the solver manager.
      if self._verbose is True:
         print "Constructing solver manager of type="+self._solver_manager_type
      self._solver_manager = SolverManagerFactory(self._solver_manager_type)
      if self._solver_manager is None:
         raise ValueError, "Failed to create solver manager of type="+self._solver_manager_type+" specified in call to PH constructor"

      # a set of all valid PH iteration indicies is generally useful for plug-ins, so create it here.
      self._iteration_index_set = Set(name="PHIterations")
      for i in range(0,self._max_iterations + 1):
         self._iteration_index_set.add(i)      

      # spit out parameterization if verbosity is enabled
      if self._verbose is True:
         print "PH solver configuration: "
         print "   Max iterations=" + `self._max_iterations`
         print "   Default global rho=" + `self._rho`
         if self._rho_setter is not None:
            print "   Rho initialization file=" + self._rho_setter
         if self._bounds_setter is not None:
            print "   Variable bounds initialization file=" + self._bounds_setter            
         print "   Sub-problem solver type=" + `self._solver_type`
         print "   Solver manager type=" + `self._solver_manager_type`
         print "   Keep solver files? " + str(self._keep_solver_files)
         print "   Output solver results? " + str(self._output_solver_results)
         print "   Output solver log? " + str(self._output_solver_log)
         print "   Output times? " + str(self._output_times)
         print "   Checkpoint interval="+str(self._checkpoint_interval)

   """ Initialize PH with model and scenario data, in preparation for solve().
       Constructs and reads instances.
   """
   def initialize(self, scenario_data_directory_name=".", model=None, model_instance=None, scenario_tree=None, converger=None):

      self._init_start_time = time.time()

      if self._verbose is True:
         print "Initializing PH"
         print "   Scenario data directory=" + scenario_data_directory_name

      if not os.path.exists(scenario_data_directory_name):
         raise ValueError, "Scenario data directory=" + scenario_data_directory_name + " either does not exist or cannot be read"

      self._scenario_data_directory_name = scenario_data_directory_name

      # IMPT: The input model should be an *instance*, as it is very useful (critical!) to know
      #       the dimensions of sets, be able to store suffixes on variable values, etc.
      if model is None:
         raise ValueError, "A model must be supplied to the PH initialize() method"

      if scenario_tree is None:
         raise ValueError, "A scenario tree must be supplied to the PH initialize() method"

      if converger is None:
         raise ValueError, "A convergence computer must be supplied to the PH initialize() method"

      self._model = model
      self._model_instance = model_instance
      self._scenario_tree = scenario_tree
      self._converger = converger

      model_objective = model.active_components(Objective)
      self._is_minimizing = (model_objective[ model_objective.keys()[0] ].sense == minimize)

      self._converger.reset()

      # construct the instances for each scenario
      if self._verbose is True:
         if self._scenario_tree._scenario_based_data == 1:
            print "Scenario-based instance initialization enabled"
         else:
            print "Node-based instance initialization enabled"
         
      for scenario in self._scenario_tree._scenarios:

         scenario_instance = None

         if self._verbose is True:
            print "Creating instance for scenario=" + scenario._name

         try:
            if self._scenario_tree._scenario_based_data == 1:
               scenario_data_filename = self._scenario_data_directory_name + os.sep + scenario._name + ".dat"
               if self._verbose is True:
                  print "Data for scenario=" + scenario._name + " loads from file=" + scenario_data_filename
               scenario_instance = (self._model).create(scenario_data_filename)
            else:
               scenario_instance = self._model.clone()
               scenario_data = ModelData()
               current_node = scenario._leaf_node
               while current_node is not None:
                  node_data_filename = self._scenario_data_directory_name + os.sep + current_node._name + ".dat"
                  if self._verbose is True:
                     print "Node data for scenario=" + scenario._name + " partially loading from file=" + node_data_filename
                  scenario_data.add_data_file(node_data_filename)
                  current_node = current_node._parent
               scenario_data.read(model=scenario_instance)
               scenario_instance._load_model_data(scenario_data)
               scenario_instance.presolve()
         except:
            print "Encountered exception in model instance creation - traceback:"
            traceback.print_exc()
            raise RuntimeError, "Failed to create model instance for scenario=" + scenario._name

         self._instances[scenario._name] = scenario_instance
         self._instances[scenario._name].name = scenario._name
         self._instance_augmented_attributes[scenario._name] = []

      # create ph-specific parameters (weights, xbar, etc.) for each instance.

      if self._verbose is True:
         print "Creating weight, average, and rho parameter vectors for scenario instances"

      self._create_ph_scenario_parameters()
            
      # if specified, run the user script to initialize variable rhos at their whim.
      if self._rho_setter is not None:
         print "Executing user rho set script from filename=", self._rho_setter
         execfile(self._rho_setter)

      # with the instances created, run the user script to initialize variable bounds.
      if self._bounds_setter is not None:
         print "Executing user variable bounds set script from filename=", self._bounds_setter
         execfile(self._bounds_setter)

      # create parameters to store variable statistics (of general utility) at each node in the scenario tree.

      if self._verbose is True:
         print "Creating variable statistic (min/avg/max) parameter vectors for scenario tree nodes"

      for stage in self._scenario_tree._stages[:-1]:

         # first, gather all unique variables referenced in this stage
         # this "gather" step is currently required because we're being lazy
         # in terms of index management in the scenario tree - which
         # should really be done in terms of sets of indices.

         stage_variables = {}
         for (reference_variable, index_template, reference_index) in stage._variables:
            if reference_variable.name not in stage_variables.keys():
               stage_variables[reference_variable.name] = reference_variable

         # next, create min/avg/max parameters for each variable in the corresponding tree node.
         # NOTE: the parameter names below could really be empty, as they are never referenced
         #       explicitly.
         for (variable_name, reference_variable) in stage_variables.items():
            for tree_node in stage._tree_nodes:

               new_min_index = reference_variable._index 
               new_min_parameter_name = "NODEMIN_"+reference_variable.name
               new_min_parameter = Param(new_min_index,name=new_min_parameter_name)
               for index in new_min_index:
                  new_min_parameter[index] = 0.0
               tree_node._minimums[reference_variable.name] = new_min_parameter                                    

               new_avg_index = reference_variable._index 
               new_avg_parameter_name = "NODEAVG_"+reference_variable.name
               new_avg_parameter = Param(new_avg_index,name=new_avg_parameter_name)
               for index in new_avg_index:
                  new_avg_parameter[index] = 0.0
               tree_node._averages[reference_variable.name] = new_avg_parameter

               new_max_index = reference_variable._index 
               new_max_parameter_name = "NODEMAX_"+reference_variable.name
               new_max_parameter = Param(new_max_index,name=new_max_parameter_name)
               for index in new_max_index:
                  new_max_parameter[index] = 0.0
               tree_node._maximums[reference_variable.name] = new_max_parameter

      # the objective functions are modified throughout the course of PH iterations.
      # save the original, as a baseline to modify in subsequent iterations. reserve
      # the original objectives, for subsequent modification. 
      self._original_objective_expression = {}
      for instance_name, instance in self._instances.items():
         objective_name = instance.active_components(Objective).keys()[0]
         self._original_objective_expression[instance_name] = instance.active_components(Objective)[objective_name]._data[None].expr

      # cache the number of discrete and continuous variables in the master instance. this value
      # is of general use, e.g., in the converger classes and in plugins.
      (self._total_discrete_vars,self._total_continuous_vars) = self.compute_variable_counts()
      if self._verbose is True:
         print "Total number of discrete instance variables="+str(self._total_discrete_vars)
         print "Total number of continuous instance variables="+str(self._total_continuous_vars)

      # track the total number of fixed variables of each category at the end of each PH iteration.
      (self._total_fixed_discrete_vars,self._total_fixed_continuous_vars) = self.compute_fixed_variable_counts()

      # indicate that we're ready to run.
      self._initialized = True

      if self._verbose is True:
         print "PH successfully created model instances for all scenarios"

      self._init_end_time = time.time()

      if self._verbose is True:
         print "PH is successfully initialized"
         if self._output_times is True:
            print "Initialization time=%8.2f seconds" % (self._init_end_time - self._init_start_time)

      # let plugins know if they care.
      if self._verbose is True:
         print "Initializing PH plugins"
      for plugin in self._ph_plugins:
         plugin.post_ph_initialization(self)
      if self._verbose is True:
         print "PH plugin initialization complete"

   """ Perform the non-weighted scenario solves and form the initial w and xbars.
   """   
   def iteration_0_solve(self):

      if self._verbose is True:
         print "------------------------------------------------"
         print "Starting PH iteration 0 solves"

      self._current_iteration = 0

      solve_start_time = time.time()

      # STEP 0: set up all global solver options.
      self._solver.mipgap = self._mipgap

      # STEP 1: queue up the solves for all scenario sub-problems and
      #         grab all the action handles for the subsequent barrier sync.

      action_handles = []
      action_handle_instance_map = {}

      for scenario in self._scenario_tree._scenarios:
         
         instance = self._instances[scenario._name]
         
         if self._verbose is True:
            print "Queuing solve for scenario=" + scenario._name

         # IMPT: You have to re-presolve if approximating continuous variable penalty terms with a
         #       piecewise linear function. otherwise, the newly introduced variables won't be flagged
         #       as unused (as is correct for iteration 0), and the output writer will crater.
         if self._linearize_nonbinary_penalty_terms > 0:
           instance.presolve()            
            
         # there's nothing to warm-start from in iteration 0, so don't include the keyword in the solve call.
         # the reason you don't want to include it is that some solvers don't know how to handle the keyword 
         # at all (despite it being false). you might want to solve iteration 0 solves using some other solver.

         new_action_handle = self._solver_manager.queue(instance, opt=self._solver, tee=self._output_solver_log)
         action_handle_instance_map[scenario._name] = new_action_handle

         action_handles.append(new_action_handle)

      # STEP 2: barrier sync for all scenario sub-problem solves.
      if self._verbose is True:
         print "Waiting for scenario sub-problem solves"
      self._solver_manager.wait_all(action_handles)
      if self._verbose is True:      
         print "Scenario sub-problem solves completed"      

      solve_end_time = time.time()
      self._cumulative_solve_time += (solve_end_time - solve_start_time)

      if self._output_times is True:
         print "Aggregate sub-problem solve time=%8.2f" % (solve_end_time - solve_start_time)

      # STEP 3: Load the results!
      for scenario_name, action_handle in action_handle_instance_map.items():

         if self._verbose is True:         
            print "Successfully processed results for scenario="+scenario_name

         instance = self._instances[scenario_name]
         results = self._solver_manager.get_results(action_handle)

         if len(results.solution) == 0:
            results.write(num=1)
            raise RuntimeError, "Solve failed for scenario="+scenario_name+"; no solutions generated"

         if self._output_solver_results is True:
            print "Results for scenario=",scenario_name
            results.write(num=1)            

         instance.load(results)

         if self._verbose is True:                  
            print "Successfully loaded solution for scenario="+scenario_name

      if self._verbose is True:
         print "Successfully completed PH iteration 0 solves - solution statistics:"
         print "         Scenario              Objective                  Value"
         for scenario in self._scenario_tree._scenarios:
            instance = self._instances[scenario._name]
            for objective_name in instance.active_components(Objective):
               objective = instance.active_components(Objective)[objective_name]
               print "%20s       %15s     %14.4f" % (scenario._name, objective.name, objective._data[None].expr())
         print "------------------------------------------------"

   #
   # recompute the averages, minimum, and maximum statistics for all variables to be blended by PH, i.e.,
   # not appearing in the final stage. technically speaking, the min/max aren't required by PH, but they
   # are used often enough to warrant their computation and it's basically free if you're computing the
   # average.
   #
   def update_variable_statistics(self):

      start_time = time.time()
      
      for stage in self._scenario_tree._stages[:-1]: # no blending over the final stage
         
         for tree_node in stage._tree_nodes:
               
            for (variable, index_template, variable_indices) in stage._variables:
                  
               variable_name = variable.name
                     
               avg_parameter_name = "PHAVG_"+variable_name
                  
               for index in variable_indices:
                  min = float("inf")
                  avg = 0.0
                  max = float("-inf")
                  node_probability = 0.0
                     
                  is_used = True # until proven otherwise                     
                  for scenario in tree_node._scenarios:
                        
                     instance = self._instances[scenario._name]
                        
                     if getattr(instance,variable_name)[index].status == VarStatus.unused:
                        is_used = False
                     else:                        
                        node_probability += scenario._probability
                        var_value = getattr(instance, variable.name)[index].value
                        if var_value < min:
                           min = var_value
                        avg += (scenario._probability * var_value)
                        if var_value > max:
                           max = var_value

                  if is_used is True:
                     tree_node._minimums[variable.name][index] = min
                     tree_node._averages[variable.name][index] = avg / node_probability
                     tree_node._maximums[variable.name][index] = max                        

                     # distribute the newly computed average to the xbar variable in
                     # each instance/scenario associated with this node. only do this
                     # if the variable is used!
                     for scenario in tree_node._scenarios:
                        instance = self._instances[scenario._name]
                        avg_parameter = getattr(instance, avg_parameter_name)
                        avg_parameter[index] = avg / node_probability

      end_time = time.time()
      self._cumulative_xbar_time += (end_time - start_time)

   def update_weights(self):

      # because the weight updates rely on the xbars, and the xbars are node-based,
      # I'm looping over the tree nodes and pushing weights into the corresponding scenarios.
      start_time = time.time()      

      for stage in self._scenario_tree._stages[:-1]: # no blending over the final stage, so no weights to worry about.
         
         for tree_node in stage._tree_nodes:

            for (variable, index_template, variable_indices) in stage._variables:

               variable_name = variable.name
               blend_parameter_name = "PHBLEND_"+variable_name
               weight_parameter_name = "PHWEIGHT_"+variable_name
               rho_parameter_name = "PHRHO_"+variable_name

               for index in variable_indices:

                  tree_node_average = tree_node._averages[variable.name][index]()

                  for scenario in tree_node._scenarios:

                     instance = self._instances[scenario._name]

                     if getattr(instance,variable.name)[index].status != VarStatus.unused:

                        # we are currently not updating weights if blending is disabled for a variable.
                        # this is done on the premise that unless you are actively trying to move
                        # the variable toward the mean, the weights will blow up and be huge by the
                        # time that blending is activated.
                        variable_blend_indicator = getattr(instance, blend_parameter_name)[index]()                              

                        # get the weight and rho parameters for this variable/index combination.
                        rho_value = getattr(instance, rho_parameter_name)[index]()
                        current_variable_weight = getattr(instance, weight_parameter_name)[index]()
                                               
                        # if I'm maximizing, invert value prior to adding (hack to implement negatives).
                        # probably fixed in Pyomo at this point - I just haven't checked in a long while.
                        if self._is_minimizing is False:
                           current_variable_weight = (-current_variable_weight)
                        current_variable_value = getattr(instance,variable.name)[index]()
                        new_variable_weight = current_variable_weight + variable_blend_indicator * rho_value * (current_variable_value - tree_node_average)
                        # I have the correct updated value, so now invert if maximizing.
                        if self._is_minimizing is False:
                           new_variable_weight = (-new_variable_weight)
                        getattr(instance, weight_parameter_name)[index].value = new_variable_weight

      # we shouldn't have to re-simplify the expression, as we aren't adding any constant-variable terms - just modifying parameters.

      end_time = time.time()
      self._cumulative_weight_time += (end_time - start_time)

   def form_iteration_k_objectives(self):

      # for each blended variable (i.e., those not appearing in the final stage),
      # add the linear and quadratic penalty terms to the objective.
      for instance_name, instance in self._instances.items():
         
         objective_name = instance.active_components(Objective).keys()[0]         
         objective = instance.active_components(Objective)[objective_name]
         # clone the objective, because we're going to augment (repeatedly) the original objective.
         objective_expression = self._original_objective_expression[instance_name].clone() 
         # the quadratic expression is really treated as just a list - eventually should be treated as a full expression.
         quad_expression = 0.0
         
         for stage in self._scenario_tree._stages[:-1]: # skip the last stage, as no blending occurs

            variable_tree_node = None
            for node in stage._tree_nodes:
               for scenario in node._scenarios:
                  if scenario._name == instance_name:
                     variable_tree_node = node
                     break

            for (reference_variable, index_template, variable_indices) in stage._variables:

               variable_name = reference_variable.name
               variable_type = reference_variable.domain

               w_parameter_name = "PHWEIGHT_"+variable_name
               w_parameter = instance.active_components(Param)[w_parameter_name]
                  
               average_parameter_name = "PHAVG_"+variable_name
               average_parameter = instance.active_components(Param)[average_parameter_name]

               rho_parameter_name = "PHRHO_"+variable_name
               rho_parameter = instance.active_components(Param)[rho_parameter_name]

               blend_parameter_name = "PHBLEND_"+variable_name
               blend_parameter = instance.active_components(Param)[blend_parameter_name]

               node_min_parameter = variable_tree_node._minimums[variable_name]
               node_max_parameter = variable_tree_node._maximums[variable_name]               

               quad_penalty_term_variable = None
               if self._linearize_nonbinary_penalty_terms > 0:
                  quad_penalty_term_variable_name = "PHQUADPENALTY_"+variable_name
                  quad_penalty_term_variable = instance.active_components(Var)[quad_penalty_term_variable_name]

               instance_variable = instance.active_components(Var)[variable_name]

               for index in variable_indices:

                  if (instance_variable[index].status is not VarStatus.unused) and (instance_variable[index].fixed is False):

                     # add the linear (w-weighted) term is a consistent fashion, independent of variable type. 
                     # if maximizing, here is where you would want "-=" - however, if you do this, the collect/simplify process chokes for reasons currently unknown.
                     objective_expression += (w_parameter[index] * instance_variable[index])

                     # there are some cases in which a user may want to avoid the proximal term completely.
                     # it's of course only a good idea when there are at least bounds (both lb and ub) on
                     # the variables to be blended.
                     if self._drop_proximal_terms is False:

                        # deal with binaries
                        if isinstance(variable_type, BooleanSet) is True:

                           if self._retain_quadratic_binary_terms is False:
                              # this rather ugly form of the linearized quadratic expression term is required
                              # due to a pyomo bug - the form (rho/2) * (x+y+z) chokes in presolve when distributing
                              # over the sum.
                              new_term = (blend_parameter[index] * rho_parameter[index] / 2.0 * instance_variable[index]) - \
                                         (blend_parameter[index] * rho_parameter[index] * average_parameter[index] * instance_variable[index]) + \
                                         (blend_parameter[index] * rho_parameter[index] / 2.0 * average_parameter[index] * average_parameter[index])                              
                              if objective.sense is minimize:
                                 objective_expression += new_term
                              else:
                                 objective_expression -= new_term                                 
                           else:
                              quad_expression += (blend_parameter[index] * rho_parameter[index] * (instance_variable[index] - average_parameter[index]) ** 2)

                        # deal with everything else
                        else:

                           if self._linearize_nonbinary_penalty_terms > 0:

                              # the variables are easy - just a single entry.
                              if objective.sense is minimize:
                                 objective_expression += (rho_parameter[index] / 2.0 * quad_penalty_term_variable[index])
                              else:
                                 objective_expression -= (rho_parameter[index] / 2.0 * quad_penalty_term_variable[index])
                                 
                              # the constraints are somewhat nastier.

                              # TBD - DEFINE CONSTRAINTS ON-THE-FLY?? (INDIVIDUALLY NAMED FOR NOW - CREATE INDEX SETS!) - OR A LEAST AN INDEX SET PER "PIECE"
                              xavg = average_parameter[index]
                              x = instance_variable[index]

                              lb = None
                              ub = None

                              if x.lb is None:
                                 raise ValueError, "No lower bound specified for variable="+variable_name+indexToString(index)+"; required when piece-wise approximating quadratic penalty terms"
                              else:
                                 lb = x.lb()

                              if x.ub is None:
                                 raise ValueError, "No upper bound specified for variable="+variable_name+indexToString(index)+"; required when piece-wise approximating quadratic penalty terms"
                              else:
                                 ub = x.ub()

                              if x.lb == x.ub:
                                 print "***WARNING - LB EQUALS UB"
                                 print "VALUE=",x.lb
                                 print "VARIABLE="+variable_name+indexToString(index)

                              node_min = node_min_parameter[index]()
                              node_max = node_max_parameter[index]()

                              # compute the breakpoint sequence according to the specified strategy.
                              breakpoints = []
                              if self._breakpoint_strategy == 0:
                                 breakpoints = self.compute_uniform_breakpoints(lb, node_min, xavg(), node_max, ub, self._linearize_nonbinary_penalty_terms)
                              elif self._breakpoint_strategy == 1:
                                 breakpoints = self.compute_uniform_between_nodestat_breakpoints(lb, node_min, xavg(), node_max, ub, self._linearize_nonbinary_penalty_terms)
                              elif self._breakpoint_strategy == 2:
                                 breakpoints = self.compute_uniform_between_woodruff_breakpoints(lb, node_min, xavg(), node_max, ub, self._linearize_nonbinary_penalty_terms)
                              elif self._breakpoint_strategy == 3:
                                 breakpoints = self.compute_exponential_from_mean_breakpoints(lb, node_min, xavg(), node_max, ub, self._linearize_nonbinary_penalty_terms)                                                                                                   
                              else:
                                 raise ValueError, "A breakpoint distribution strategy="+str(self._breakpoint_strategy)+" is currently not supported within PH!"

                              for i in range(0,len(breakpoints)-1):

                                 this_lb = breakpoints[i]
                                 this_ub = breakpoints[i+1]

                                 piece_constraint_name = "QUAD_PENALTY_PIECE_"+str(i)+"_"+variable_name+str(index)
                                 if hasattr(instance, piece_constraint_name) is False:
                                    # this is the first time the constraint is being added - add it to the list of PH-specific constraints for this instance.
                                    self._instance_augmented_attributes[instance_name].append(piece_constraint_name)                                                                           
                                 piece_constraint = Constraint(name=piece_constraint_name)
                                 piece_constraint.model = instance
                                 piece_expression = self._create_piecewise_constraint_expression(this_lb, this_ub, x, xavg, quad_penalty_term_variable[index])
                                 piece_constraint.add(None, piece_expression)
                                 setattr(instance, piece_constraint_name, piece_constraint)                                    

                           else:

                              quad_expression += (blend_parameter[index] * rho_parameter[index] * (instance_variable[index] - average_parameter[index]) ** 2)                           
                   
         # strictly speaking, this probably isn't necessary - parameter coefficients won't get
         # pre-processed out of the expression tree. however, if the under-the-hood should change,
         # we'll be covered.
         objective_expression.simplify(instance)
         instance.active_components(Objective)[objective_name]._data[None].expr = objective_expression
         # if we are linearizing everything, then nothing will appear in the quadratic expression -
         # don't add the empty "0.0" expression to the objective. otherwise, the output file won't
         # be properly generated.
         if quad_expression != 0.0:
           instance.active_components(Objective)[objective_name]._quad_subexpr = quad_expression

   def iteration_k_solve(self):

     if self._verbose is True:
        print "------------------------------------------------"        
        print "Starting PH iteration " + str(self._current_iteration) + " solves"

     # cache the objective values generated by PH for output at the end of this function.
     ph_objective_values = {}

     solve_start_time = time.time()

     # STEP 0: set up all global solver options.
     self._solver.mipgap = self._mipgap     

     # STEP 1: queue up the solves for all scenario sub-problems and 
     #         grab all of the action handles for the subsequent barrier sync.

     action_handles = []
     action_handle_instance_map = {}

     for scenario in self._scenario_tree._scenarios:     

        instance = self._instances[scenario._name]

        if self._verbose is True:
           print "Queuing solve for scenario=" + scenario._name

        # IMPT: You have to re-presolve, as the simple presolver collects the linear terms together. If you
        # don't do this, you won't see any chance in the output files as you vary the problem parameters!
        # ditto for instance fixing!
        instance.presolve()

        # once past iteration 0, there is always a feasible solution from which to warm-start.
        # however, you might want to disable warm-start when the solver is behaving badly (which does happen).
        new_action_handle = None
        if (self._disable_warmstarts is False) and (self._solver.warm_start_capable() is True):
           new_action_handle = self._solver_manager.queue(instance, opt=self._solver, warmstart=True, tee=self._output_solver_log)
        else:
           new_action_handle = self._solver_manager.queue(instance, opt=self._solver, tee=self._output_solver_log)           

        action_handle_instance_map[scenario._name] = new_action_handle

        action_handles.append(new_action_handle)

     # STEP 2: barrier sync for all scenario sub-problem solves.
     if self._verbose is True:           
        print "Waiting for scenario sub-problem solves"
     self._solver_manager.wait_all(action_handles)
     if self._verbose is True:                
        print "Scenario sub-problem solves completed"
        
     solve_end_time = time.time()
     self._cumulative_solve_time += (solve_end_time - solve_start_time)

     if self._output_times is True:
        print "Aggregate sub-problem solve time=%8.2f" % (solve_end_time - solve_start_time)

     # STEP 3: Load the results!
     for scenario_name, action_handle in action_handle_instance_map.items():

        if self._verbose is True:         
           print "Successfully processed results for scenario="+scenario_name

        instance = self._instances[scenario_name]
        results = self._solver_manager.get_results(action_handle)

        if len(results.solution) == 0:
           raise RuntimeError, "Solve failed for scenario="+scenario_name+"; no solutions generated"

        if self._output_solver_results is True:
           print "Results for scenario=", scenario_name
           results.write(num=1)            

        instance.load(results)

        if self._verbose is True:                  
           print "Successfully loaded solution for scenario="+scenario_name

        # we're assuming there is a single solution.
        # the "value" attribute is a pre-defined feature of any solution - it is relative to whatever
        # objective was selected during optimization, which of course should be the PH objective.
        ph_objective_values[instance.name] = float(results.solution(0).objective['f'].value)

     if self._verbose is True:
        print "Successfully completed PH iteration " + str(self._current_iteration) + " solves - solution statistics:"
        print "  Scenario             PH Objective             Cost Objective"
        for scenario in self._scenario_tree._scenarios:
           instance = self._instances[scenario._name]
           for objective_name in instance.active_components(Objective):
              objective = instance.active_components(Objective)[objective_name]
              print "%20s       %18.4f     %14.4f" % (scenario._name, ph_objective_values[scenario._name], 0.0)

   def solve(self):

      self._solve_start_time = time.time()
      self._cumulative_solve_time = 0.0
      self._cumulative_xbar_time = 0.0
      self._cumulative_weight_time = 0.0

      print "Starting PH"

      if self._initialized == False:
         raise RuntimeError, "PH is not initialized - cannot invoke solve() method"

      print "Initiating PH iteration=" + `self._current_iteration`

      self.iteration_0_solve()

      # update variable statistics prior to any output.
      self.update_variable_statistics()      

      if self._verbose is True:
         print "Variable values following scenario solves:"
         self.pprint(False,False,True,False)

      # let plugins know if they care.
      for plugin in self._ph_plugins:      
         plugin.post_iteration_0_solves(self)

      # update the fixed variable statistics.
      (self._total_fixed_discrete_vars,self._total_fixed_continuous_vars) = self.compute_fixed_variable_counts()               

      if self._verbose is True:
         print "Number of discrete variables fixed="+str(self._total_fixed_discrete_vars)+" (total="+str(self._total_discrete_vars)+")"
         print "Number of continuous variables fixed="+str(self._total_fixed_continuous_vars)+" (total="+str(self._total_continuous_vars)+")"

      self._converger.update(self._current_iteration, self, self._scenario_tree, self._instances)
      print "Convergence metric=%12.4f" % self._converger.lastMetric()

      self.update_weights()

      # let plugins know if they care.
      for plugin in self._ph_plugins:      
         plugin.post_iteration_0(self)

      # checkpoint if it's time - which it always is after iteration 0,
      # if the interval is >= 1!
      if (self._checkpoint_interval > 0):
         self.checkpoint(0)

      # there is an upper bound on the number of iterations to execute -
      # the actual bound depends on the converger supplied by the user.
      for i in range(1, self._max_iterations+1):

         self._current_iteration = self._current_iteration + 1                  

         print "Initiating PH iteration=" + `self._current_iteration`         

         if self._verbose is True:
            print "Variable averages and weights prior to scenario solves:"
            self.pprint(True,True,False,False)

         # with the introduction of piecewise linearization, the form of the
         # penalty-weighted objective is no longer fixed. thus, we need to
         # create the objectives each PH iteration.
         self.form_iteration_k_objectives()            

         self.iteration_k_solve()

         # update variable statistics prior to any output.
         self.update_variable_statistics()
         
         if self._verbose is True:
            print "Variable values following scenario solves:"
            self.pprint(False,False,True,False)

         # we don't technically have to do this at the last iteration,
         # but with checkpointing and re-starts, you're never sure 
         # when you're executing the last iteration.
         self.update_weights()

         # let plugins know if they care.
         for plugin in self._ph_plugins:
            plugin.post_iteration_k_solves(self)

         # update the fixed variable statistics.
         (self._total_fixed_discrete_vars,self._total_fixed_continuous_vars) = self.compute_fixed_variable_counts()               

         if self._verbose is True:
            print "Number of discrete variables fixed="+str(self._total_fixed_discrete_vars)+" (total="+str(self._total_discrete_vars)+")"
            print "Number of continuous variables fixed="+str(self._total_fixed_continuous_vars)+" (total="+str(self._total_continuous_vars)+")"

         # let plugins know if they care.
         for plugin in self._ph_plugins:
            plugin.post_iteration_k(self)

         # at this point, all the real work of an iteration is complete.

         # checkpoint if it's time.
         if (self._checkpoint_interval > 0) and (i % self._checkpoint_interval is 0):
            self.checkpoint(i)

         # check for early termination.
         self._converger.update(self._current_iteration, self, self._scenario_tree, self._instances)
         print "Convergence metric=%12.4f" % self._converger.lastMetric()

         if self._converger.isConverged(self) is True:
            if self._total_discrete_vars == 0:
               print "PH converged - convergence metric is below threshold="+str(self._converger._convergence_threshold)
            else:
               print "PH converged - convergence metric is below threshold="+str(self._converger._convergence_threshold)+" or all discrete variables are fixed"               
            break

         # if we're terminating due to exceeding the maximum iteration count, print a message
         # indicating so - otherwise, you get a quiet, information-free output trace.
         if i == self._max_iterations:
            print "Halting PH - reached maximal iteration count="+str(self._max_iterations)

      if self._verbose is True:
         print "Number of discrete variables fixed before final plugin calls="+str(self._total_fixed_discrete_vars)+" (total="+str(self._total_discrete_vars)+")"
         print "Number of continuous variables fixed before final plugin calls="+str(self._total_fixed_continuous_vars)+" (total="+str(self._total_continuous_vars)+")"            

      # let plugins know if they care. do this before
      # the final solution / statistics output, as the plugins
      # might do some final tweaking.
      for plugin in self._ph_plugins:
         plugin.post_ph_execution(self)

      # update the fixed variable statistics - the plugins might have done something.
      (self._total_fixed_discrete_vars,self._total_fixed_continuous_vars) = self.compute_fixed_variable_counts()                        

      print "PH complete"

      print "Convergence history:"
      self._converger.pprint()

      print "Final number of discrete variables fixed="+str(self._total_fixed_discrete_vars)+" (total="+str(self._total_discrete_vars)+")"
      print "Final number of continuous variables fixed="+str(self._total_fixed_continuous_vars)+" (total="+str(self._total_continuous_vars)+")"         

      print "Final variable values:"
      self.pprint(False,False,True,True)         

      print "Final costs:"
      self._scenario_tree.pprintCosts(self._instances)

      self._solve_end_time = time.time()

      if (self._verbose is True) and (self._output_times is True):
         print "Overall run-time=   %8.2f seconds" % (self._solve_end_time - self._solve_start_time)

      # cleanup the scenario instances for post-processing - ideally, we want to leave them in
      # their original state, minus all the PH-specific stuff. we don't do all cleanup (leaving
      # things like rhos, etc), but we do clean up constraints, as that really hoses up the ef writer.
      self._cleanup_scenario_instances()

   #
   # prints a summary of all collected time statistics
   #
   def print_time_stats(self):

      print "PH run-time statistics (user):"

      print "Initialization time=  %8.2f seconds" % (self._init_end_time - self._init_start_time)
      print "Overall solve time=   %8.2f seconds" % (self._solve_end_time - self._solve_start_time)
      print "Scenario solve time=  %8.2f seconds" % self._cumulative_solve_time
      print "Average update time=  %8.2f seconds" % self._cumulative_xbar_time
      print "Weight update time=   %8.2f seconds" % self._cumulative_weight_time

   #
   # a utility to determine whether to output weight / average / etc. information for
   # a variable/node combination. when the printing is moved into a callback/plugin,
   # this routine will go there. for now, we don't dive down into the node resolution -
   # just the variable/stage.
   #
   def should_print(self, stage, variable, variable_indices):

      if self._output_continuous_variable_stats is False:

         variable_type = variable.domain         

         if (isinstance(variable_type, IntegerSet) is False) and (isinstance(variable_type, BooleanSet) is False):

            return False

      return True
      
   #
   # pretty-prints the state of the current variable averages, weights, and values.
   # inputs are booleans indicating which components should be output.
   #
   def pprint(self, output_averages, output_weights, output_values, output_fixed):

      if self._initialized is False:
         raise RuntimeError, "PH is not initialized - cannot invoke pprint() method"         
      
      # print tree nodes and associated variable/xbar/ph information in stage-order
      # we don't blend in the last stage, so we don't current care about printing the associated information.
      for stage in self._scenario_tree._stages[:-1]:

         print "\tStage=" + stage._name

         num_outputs_this_stage = 0 # tracks the number of outputs on a per-index basis.

         for (variable, index_template, variable_indices) in stage._variables:

            variable_name = variable.name

            if self.should_print(stage, variable, variable_indices) is True:

               num_outputs_this_variable = 0 # track, so we don't output the variable names unless there is an entry to report.

               for index in variable_indices:               

                  weight_parameter_name = "PHWEIGHT_"+variable_name

                  num_outputs_this_index = 0 # track, so we don't output the variable index more than once.

                  for tree_node in stage._tree_nodes:                  

                     # determine if the variable/index pair is used across the set of scenarios (technically,
                     # it should be good enough to check one scenario). ditto for "fixed" status. fixed does
                     # imply unused (see note below), but we care about the fixed status when outputting
                     # final solutions.

                     is_used = True # should be consistent across scenarios, so one "unused" flags as invalid.
                     is_fixed = False

                     for scenario in tree_node._scenarios:
                        instance = self._instances[scenario._name]
                        variable_value = getattr(instance,variable_name)[index]
                        if variable_value.status == VarStatus.unused:
                           is_used = False
                        if variable_value.fixed is True:
                           is_fixed = True
 
                     # IMPT: this is far from obvious, but variables that are fixed will - because
                     #       presolve will identify them as constants and eliminate them from all
                     #       expressions - be flagged as "unused" and therefore not output.

                     if ((output_fixed is True) and (is_fixed is True)) or (is_used is True):

                           minimum_value = tree_node._minimums[variable_name][index]()
                           maximum_value = tree_node._maximums[variable_name][index]()

                           num_outputs_this_stage = num_outputs_this_stage + 1                           
                           num_outputs_this_variable = num_outputs_this_variable + 1
                           num_outputs_this_index = num_outputs_this_index + 1

                           if num_outputs_this_variable == 1:
                              print "\t\tVariable=",variable_name

                           if num_outputs_this_index == 1:
                              print "\t\t\tIndex:", indexToString(index)                              

                           print "\t\t\t\tTree Node=",tree_node._name,"\t\t (Scenarios: ",                              
                           for scenario in tree_node._scenarios:
                              print scenario._name," ",
                              if scenario == tree_node._scenarios[-1]:
                                 print ")"
                           
                           if output_values is True:
                              average_value = tree_node._averages[variable_name][index]()
                              print "\t\t\t\tValues: ",                        
                              for scenario in tree_node._scenarios:
                                 instance = self._instances[scenario._name]
                                 this_value = getattr(instance,variable_name)[index].value
                                 print "%12.4f" % this_value,
                                 if scenario == tree_node._scenarios[-1]:
                                    print "    Max-Min=%12.4f" % (maximum_value-minimum_value),
                                    print "    Avg=%12.4f" % (average_value),
                                    print ""
                           if output_weights:
                              print "\t\t\t\tWeights: ",
                              for scenario in tree_node._scenarios:
                                 instance = self._instances[scenario._name]
                                 print "%12.4f" % getattr(instance,weight_parameter_name)[index].value,
                                 if scenario == tree_node._scenarios[-1]:
                                    print ""

                           if output_averages:
                              print "\t\t\t\tAverage: %12.4f" % (tree_node._averages[variable_name][index].value)

         if num_outputs_this_stage == 0:
            print "\t\tNo non-converged variables in stage"

         # cost variables aren't blended, so go through the gory computation of min/max/avg.
         # we currently always print these.
         cost_variable_name = stage._cost_variable[0].name
         cost_variable_index = stage._cost_variable[1]
         if cost_variable_index is None:
            print "\t\tCost Variable=" + cost_variable_name
         else:
            print "\t\tCost Variable=" + cost_variable_name + indexToString(cost_variable_index)            
         for tree_node in stage._tree_nodes:
            print "\t\t\tTree Node=" + tree_node._name + "\t\t (Scenarios: ",
            for scenario in tree_node._scenarios:
               print scenario._name," ",
               if scenario == tree_node._scenarios[-1]:
                  print ")"
            maximum_value = 0.0
            minimum_value = 0.0
            sum_values = 0.0
            num_values = 0
            first_time = True
            print "\t\t\tValues: ",                        
            for scenario in tree_node._scenarios:
                instance = self._instances[scenario._name]
                this_value = getattr(instance,cost_variable_name)[cost_variable_index].value
                print "%12.4f" % this_value,
                num_values += 1
                sum_values += this_value
                if first_time is True:
                   first_time = False
                   maximum_value = this_value
                   minimum_value = this_value
                else:
                   if this_value > maximum_value:
                      maximum_value = this_value
                   if this_value < minimum_value:
                      minimum_value = this_value
                if scenario == tree_node._scenarios[-1]:
                   print "    Max-Min=%12.4f" % (maximum_value-minimum_value),
                   print "    Avg=%12.4f" % (sum_values/num_values),
                   print ""
            
