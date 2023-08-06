import pyutilib
import sys
import os
import time
import traceback
import copy

from coopr.pysp.scenariotree import *
from coopr.pysp.convergence import *
from coopr.pysp.ph import *

from coopr.pyomo.base import *
from coopr.pyomo.io import *

from coopr.pyomo.base.var import _VarValue, _VarBase

# brain-dead utility for determing if there is a binary to write in the 
# composite model - need to know this, because CPLEX doesn't like empty
# binary blocks in the LP file.
def binaries_present(master_model, scenario_instances):

   # check the master model first.
   for var in master_model.active_components(Var).values():
      if isinstance(var.domain, BooleanSet):
         return True

   # scan the scenario instances next.
   for scenario_name in scenario_instances.keys():
      scenario_instance = scenario_instances[scenario_name]
      for var in scenario_instance.active_components(Var).values():
         if isinstance(var.domain, BooleanSet):
            return True

   return False

# brain-dead utility for determing if there is a binary to write in the 
# composite model - need to know this, because CPLEX doesn't like empty
# integer blocks in the LP file.
def integers_present(master_model, scenario_instances):

   # check the master model first.
   for var in master_model.active_components(Var).values():
      if isinstance(var.domain, IntegerSet):
         return True

   # scan the scenario instances next.
   for scenario_name in scenario_instances.keys():
      scenario_instance = scenario_instances[scenario_name]
      for var in scenario_instance.active_components(Var).values():
         if isinstance(var.domain, IntegerSet):
            return True

   return False

# the main extensive-form writer routine - including read of scenarios/etc.
def write_ef_from_scratch(model_directory, instance_directory, output_filename, \
                          generate_weighted_cvar, cvar_weight, risk_alpha):

   start_time = time.time()

   scenario_data_directory_name = instance_directory

   print "Initializing extensive form writer"
   print ""

   ################################################################################################
   #### INITIALIZATION ############################################################################
   ################################################################################################

   #
   # validate cvar options, if specified.
   #
   if generate_weighted_cvar is True:
      if cvar_weight <= 0.0:
         raise RuntimeError, "Weight of CVaR term must be >= 0.0 - value supplied="+str(cvar_weight)
      if (risk_alpha <= 0.0) or (risk_alpha >= 1.0):
         raise RuntimeError, "CVaR risk alpha must be between 0 and 1, exclusive - value supplied="+str(risk_alpha)

      print "Writing CVaR weighted objective"
      print "CVaR term weight="+str(cvar_weight)
      print "CVaR alpha="+str(risk_alpha)
      print ""
   
   #
   # create and populate the core model
   #
   master_scenario_model = None
   master_scenario_instance = None
   
   try:
      
      reference_model_filename = model_directory+os.sep+"ReferenceModel.py"   
      modelimport = pyutilib.misc.import_file(reference_model_filename)
      if "model" not in dir(modelimport):
         print ""
         print "Exiting ef module: No 'model' object created in module "+reference_model_filename
         sys.exit(0)
      if modelimport.model is None:
         print ""
         print "Exiting ef module: 'model' object equals 'None' in module "+reference_model_filename
         sys.exit(0)
   
      master_scenario_model = modelimport.model

   except IOError:
      
      print "***ERROR: Failed to load scenario reference model from file="+reference_model_filename
      return

   try:
      
      reference_scenario_filename = instance_directory+os.sep+"ReferenceModel.dat"
      master_scenario_instance = master_scenario_model.create(reference_scenario_filename)
      
   except IOError:
      
      print "***ERROR: Failed to load scenario reference instance data from file="+reference_instance_filename
      return            

   #
   # create and populate the scenario tree model
   #

   treeimport = pyutilib.misc.import_file(model_directory+os.sep+"ScenarioStructure.py")

   tree_data = treeimport.model.create(instance_directory+os.sep+"ScenarioStructure.dat")

   #
   # construct the scenario tree
   #
   scenario_tree = ScenarioTree(model=master_scenario_instance,
                                nodes=tree_data.Nodes,
                                nodechildren=tree_data.Children,
                                nodestages=tree_data.NodeStage,
                                nodeprobabilities=tree_data.ConditionalProbability,
                                stages=tree_data.Stages,
                                stagevariables=tree_data.StageVariables,
                                stagecostvariables=tree_data.StageCostVariable,
                                scenarios=tree_data.Scenarios,
                                scenarioleafs=tree_data.ScenarioLeafNode,
                                scenariobaseddata=tree_data.ScenarioBasedData)

   #
   # print the input tree for validation/information purposes.
   #
   scenario_tree.pprint()

   #
   # validate the tree prior to doing anything serious
   #
   print ""
   if scenario_tree.validate() is False:
      print "***Scenario tree is invalid****"
      sys.exit(1)
   else:
      print "Scenario tree is valid!"
   print ""

   #
   # construct instances for each scenario
   #

   instances = {}
   
   if scenario_tree._scenario_based_data == 1:
      print "Scenario-based instance initialization enabled"
   else:
      print "Node-based instance initialization enabled"
         
   for scenario in scenario_tree._scenarios:

      scenario_instance = None

      print "Creating instance for scenario=" + scenario._name

      try:
         if scenario_tree._scenario_based_data == 1:
            scenario_data_filename = scenario_data_directory_name + os.sep + scenario._name + ".dat"
#            print "Data for scenario=" + scenario._name + " loads from file=" + scenario_data_filename
            scenario_instance = master_scenario_model.create(scenario_data_filename)
         else:
            scenario_instance = master_scenario_model.clone()
            scenario_data = ModelData()
            current_node = scenario._leaf_node
            while current_node is not None:
               node_data_filename = scenario_data_directory_name + os.sep + current_node._name + ".dat"
#               print "Node data for scenario=" + scenario._name + " partially loading from file=" + node_data_filename
               scenario_data.add_data_file(node_data_filename)
               current_node = current_node._parent
            scenario_data.read(model=scenario_instance)
            scenario_instance._load_model_data(scenario_data)
            scenario_instance.presolve()
      except:
         print "Encountered exception in model instance creation - traceback:"
         traceback.print_exc()
         raise RuntimeError, "Failed to create model instance for scenario=" + scenario._name

      # name each instance with the scenario name, so the prefixes in the EF make sense.
      scenario_instance.name = scenario._name
      
      scenario_instance.presolve()
      instances[scenario._name] = scenario_instance

   print ""

   ################################################################################################
   #### CREATE THE MASTER / BINDING INSTANCE ######################################################
   ################################################################################################

   master_binding_instance = Model()
   master_binding_instance.name = "MASTER"

   # walk the scenario tree - create variables representing the common values for all scenarios
   # associated with that node. the constraints will be created later. also create expected-cost
   # variables for each node, to be computed via constraints/objectives defined in a subsequent pass.
   # master variables are created for all nodes but those in the last stage. expected cost variables
   # are, for no particularly good reason other than easy coding, created for nodes in all stages.
   print "Creating variables for master binding instance"

   for stage in scenario_tree._stages:

      for (stage_variable, index_template, stage_variable_indices) in stage._variables:

         print "Creating master variable and blending constraints for decision variable=", stage_variable, ", indices=", stage_variable_indices

         for tree_node in stage._tree_nodes:

            if stage != scenario_tree._stages[-1]:      

               master_variable_name = tree_node._name + "_" + stage_variable.name

               # because there may be a single stage variable and multiple indices, check
               # for the existence of the variable at this node - if you don't, you'll
               # inadvertently over-write what was there previously!
               master_variable = None
               try:
                  master_variable = getattr(master_binding_instance, master_variable_name)
               except:
                  # the deepcopy is probably too expensive (and unnecessary) computationally -
                  # easier to just use the constructor with the stage variable index/bounds/etc.
                  # NOTE: need to re-assign the master variables for each _varval - they probably
                  #       point to a bogus model.
                  new_master_variable = copy.deepcopy(stage_variable)
                  new_master_variable.name = master_variable_name
                  new_master_variable._model = master_binding_instance
                  setattr(master_binding_instance, master_variable_name, new_master_variable)

                  master_variable = new_master_variable

               for index in stage_variable_indices:

                  is_used = True # until proven otherwise                     
                  for scenario in tree_node._scenarios:
                     instance = instances[scenario._name]
                     if getattr(instance,stage_variable.name)[index].status == VarStatus.unused:
                        is_used = False

                  is_fixed = False # until proven otherwise
                  for scenario in tree_node._scenarios:
                     instance = instances[scenario._name]
                     if getattr(instance,stage_variable.name)[index].fixed is True:
                        is_fixed = True

                  if (is_used is True) and (is_fixed is False):
                           
                     # the following is necessary, specifically to get the name - deepcopy won't reset these attributes.
                     # and because presolve/simplification is name-based, the names *have* to be different.
                     master_variable[index].var = master_variable
                     master_variable[index].name = tree_node._name + "_" + master_variable[index].name

                     for scenario in tree_node._scenarios:

                        scenario_instance = instances[scenario._name]
                        scenario_variable = getattr(scenario_instance, stage_variable.name)
                        new_constraint_name = scenario._name + "_" + master_variable_name + "_" + str(index)
                        new_constraint = Constraint(name=new_constraint_name)
                        new_expr = master_variable[index] - scenario_variable[index]
                        new_constraint.add(None, (0.0, new_expr, 0.0))
                        new_constraint._model = master_binding_instance
                        setattr(master_binding_instance, new_constraint_name, new_constraint)

            # create a variable to represent the expected cost at this node -
            # the constraint to compute this comes later.
            expected_cost_variable_name = "EXPECTED_COST_" + tree_node._name
            expected_cost_variable = Var(name=expected_cost_variable_name)
            expected_cost_variable._model = master_binding_instance
            setattr(master_binding_instance, expected_cost_variable_name, expected_cost_variable)

   # if we're generating the weighted CVaR objective term, create the corresponding variable and
   # the master CVaR eta variable.
   if generate_weighted_cvar is True:
      root_node = scenario_tree._stages[0]._tree_nodes[0]
      
      cvar_cost_variable_name = "CVAR_COST_" + root_node._name
      cvar_cost_variable = Var(name=cvar_cost_variable_name)
      setattr(master_binding_instance, cvar_cost_variable_name, cvar_cost_variable)
      cvar_cost_variable.construct()

      cvar_eta_variable_name = "CVAR_ETA_" + root_node._name
      cvar_eta_variable = Var(name=cvar_eta_variable_name)
      setattr(master_binding_instance, cvar_eta_variable_name, cvar_eta_variable)      
      cvar_eta_variable.construct()

   master_binding_instance.presolve()

   # ditto above for the (non-expected) cost variable.
   for stage in scenario_tree._stages:

      (cost_variable,cost_variable_index) = stage._cost_variable

      print "Creating master variable and blending constraints for cost variable=", cost_variable, ", index=", cost_variable_index      

      for tree_node in stage._tree_nodes:

         new_cost_variable_name = tree_node._name + "_" + cost_variable.name

         # TBD - the following is bad - check to see if it's already there (I suspect some of them are!!!)

         # this is undoubtedly wasteful, in that a cost variable
         # for each tree node is created with *all* indices. 
         new_cost_variable = copy.deepcopy(cost_variable)
         new_cost_variable.name = new_cost_variable_name
         new_cost_variable._model = master_binding_instance
         setattr(master_binding_instance, new_cost_variable_name, new_cost_variable)

         # the following is necessary, specifically to get the name - deepcopy won't reset these attributes.
         new_cost_variable[cost_variable_index].var = new_cost_variable
         if cost_variable_index is not None:
            # if the variable index is None, the variable is derived from a VarValue, so the
            # name gets updated automagically.
            new_cost_variable[cost_variable_index].name = tree_node._name + "_" + new_cost_variable[cost_variable_index].name

         for scenario in tree_node._scenarios:

            scenario_instance = instances[scenario._name]
            scenario_cost_variable = getattr(scenario_instance, cost_variable.name)
            new_constraint_name = scenario._name + "_" + new_cost_variable_name + "_" + str(cost_variable_index)
            new_constraint = Constraint(name=new_constraint_name)
            new_expr = new_cost_variable[cost_variable_index] - scenario_cost_variable[cost_variable_index]
            new_constraint.add(None, (0.0, new_expr, 0.0))
            new_constraint._model = master_binding_instance
            setattr(master_binding_instance, new_constraint_name, new_constraint)

   # create the constraints for computing the master per-node cost variables,
   # i.e., the current node cost and the expected cost of the child nodes.
   # if the root, then the constraint is just the objective.

   for stage in scenario_tree._stages:

      (stage_cost_variable,stage_cost_variable_index) = stage._cost_variable

      for tree_node in stage._tree_nodes:

         node_expected_cost_variable_name = "EXPECTED_COST_" + tree_node._name
         node_expected_cost_variable = getattr(master_binding_instance, node_expected_cost_variable_name)

         node_cost_variable_name = tree_node._name + "_" + stage_cost_variable.name
         node_cost_variable = getattr(master_binding_instance, node_cost_variable_name)                        
            
         constraint_expr = node_expected_cost_variable - node_cost_variable[stage_cost_variable_index]

         for child_node in tree_node._children:

            child_node_expected_cost_variable_name = "EXPECTED_COST_" + child_node._name
            child_node_expected_cost_variable = getattr(master_binding_instance, child_node_expected_cost_variable_name)
            constraint_expr = constraint_expr - (child_node._conditional_probability * child_node_expected_cost_variable)

         new_constraint_name = "COST" + "_" + node_cost_variable_name + "_" + str(cost_variable_index)
         new_constraint = Constraint(name=new_constraint_name)
         new_constraint.add(None, (0.0, constraint_expr, 0.0))
         new_constraint._model = master_binding_instance                     
         setattr(master_binding_instance, new_constraint_name, new_constraint)

         if tree_node._parent is None:

            an_instance = instances[instances.keys()[0]]
            an_objective = an_instance.active_components(Objective)
            opt_sense = an_objective[an_objective.keys()[0]].sense

            opt_expression = node_expected_cost_variable

            if generate_weighted_cvar is True:
               cvar_cost_variable_name = "CVAR_COST_" + tree_node._name
               cvar_cost_variable = getattr(master_binding_instance, cvar_cost_variable_name)
               opt_expression += cvar_weight * cvar_cost_variable

            new_objective = Objective(name="MASTER", sense=opt_sense)
            new_objective._data[None].expr = opt_expression
            setattr(master_binding_instance, "MASTER", new_objective)

   # CVaR requires the addition of a variable per scenario to represent the cost excess,
   # and a constraint to compute the cost excess relative to eta. we also replicate (following
   # what we do for node cost variables) an eta variable for each scenario instance, and
   # require equality with the master eta variable via constraints.
   if generate_weighted_cvar is True:
      
      root_node = scenario_tree._stages[0]._tree_nodes[0]

      master_cvar_eta_variable_name = "CVAR_ETA_" + root_node._name
      master_cvar_eta_variable = getattr(master_binding_instance, master_cvar_eta_variable_name)
      
      for scenario_name in instances.keys():
         scenario_instance = instances[scenario_name]

         # unique names are required because the presolve isn't
         # aware of the "owning" models for variables.
         cvar_excess_variable_name = "CVAR_EXCESS_"+scenario_name
         cvar_excess_variable = Var(name=cvar_excess_variable_name, domain=NonNegativeReals)
         setattr(scenario_instance, cvar_excess_variable_name, cvar_excess_variable)
         cvar_excess_variable.construct()

         cvar_eta_variable_name = "CVAR_ETA"
         cvar_eta_variable = Var(name=cvar_eta_variable_name)
         setattr(scenario_instance, cvar_eta_variable_name, cvar_eta_variable)
         cvar_eta_variable.construct()

         compute_excess_constraint_name = "COMPUTE_SCENARIO_EXCESS"
         compute_excess_constraint = Constraint(name=compute_excess_constraint_name)
         compute_excess_expression = cvar_excess_variable
         for node in scenario_tree._scenario_map[scenario_name]._node_list:
            (cost_variable, cost_variable_idx) = node._stage._cost_variable
            compute_excess_expression -= getattr(scenario_instance, cost_variable.name)[cost_variable_idx]
         compute_excess_expression += cvar_eta_variable
         compute_excess_constraint.add(None, (0.0, compute_excess_expression, None))
         compute_excess_constraint._model = scenario_instance
         setattr(scenario_instance, compute_excess_constraint_name, compute_excess_constraint)

         eta_equality_constraint_name = "MASTER_ETA_EQUALITY_WITH_" + scenario_instance.name
         eta_equality_constraint = Constraint(name=eta_equality_constraint_name)
         eta_equality_expr = master_cvar_eta_variable - cvar_eta_variable
         eta_equality_constraint.add(None, (0.0, eta_equality_expr, 0.0))
         eta_equality_constraint._model = master_binding_instance
         setattr(master_binding_instance, eta_equality_constraint_name, eta_equality_constraint)

      # add the constraint to compute the master CVaR variable value. iterate
      # over scenario instances to create the expected excess component first.
      cvar_cost_variable_name = "CVAR_COST_" + root_node._name
      cvar_cost_variable = getattr(master_binding_instance, cvar_cost_variable_name)
      cvar_eta_variable_name = "CVAR_ETA_" + root_node._name
      cvar_eta_variable = getattr(master_binding_instance, cvar_eta_variable_name)
      
      cvar_cost_expression = cvar_cost_variable - cvar_eta_variable
      
      for scenario_name in instances.keys():
         scenario_instance = instances[scenario_name]
         scenario_probability = scenario_tree._scenario_map[scenario_name]._probability

         scenario_excess_variable_name = "CVAR_EXCESS_"+scenario_name
         scenario_excess_variable = getattr(scenario_instance, scenario_excess_variable_name)

         cvar_cost_expression = cvar_cost_expression - (scenario_probability * scenario_excess_variable) / (1.0 - risk_alpha)

      compute_cvar_cost_constraint_name = "COMPUTE_CVAR_COST"
      compute_cvar_cost_constraint = Constraint(name=compute_cvar_cost_constraint_name)
      compute_cvar_cost_constraint.add(None, (0.0, cvar_cost_expression, 0.0))
      compute_cvar_cost_constraint._model = master_binding_instance
      setattr(master_binding_instance, compute_cvar_cost_constraint_name, compute_cvar_cost_constraint)

   # after mucking with instances, presolve to collect terms required prior to output.         
   # IMPT: Do the scenario instances first, as the master depends on variables in the scenarios.
   for scenario_name in instances.keys():
      scenario_instance = instances[scenario_name]   
      scenario_instance.presolve()         

   master_binding_instance.presolve()

   ################################################################################################
   #### WRITE THE COMPOSITE MODEL #################################################################
   ################################################################################################

   print ""
   print "Starting to write extensive form"

   # create the output file.
   problem_writer = cpxlp.ProblemWriter_cpxlp()
   output_file = open(output_filename,"w")

   problem_writer._output_prefixes = True # we always want prefixes

   ################################################################################################
   #### WRITE THE MASTER OBJECTIVE ################################################################
   ################################################################################################

   # write the objective for the master binding instance.
   problem_writer._output_objectives = True
   problem_writer._output_constraints = False
   problem_writer._output_variables = False

   print >>output_file, "\\ Begin objective block for master"
   problem_writer._print_model_LP(master_binding_instance, output_file)
   print >>output_file, "\\ End objective block for master"
   print >>output_file, ""

   ################################################################################################
   #### WRITE THE CONSTRAINTS FOR THE MASTER MODEL AND ALL SCENARIO MODELS ########################
   ################################################################################################

   print >>output_file, "s.t."
   print >>output_file, ""
   
   problem_writer._output_objectives = False
   problem_writer._output_constraints = True
   problem_writer._output_variables = False

   print >>output_file, "\\ Begin constraint block for master"
   problem_writer._print_model_LP(master_binding_instance, output_file)
   print >>output_file, "\\ End constraint block for master",
   print >>output_file, ""

   for scenario_name in instances.keys():
      instance = instances[scenario_name]
      print >>output_file, "\\ Begin constraint block for scenario",scenario_name       
      problem_writer._print_model_LP(instance, output_file)
      print >>output_file, "\\ End constraint block for scenario",scenario_name
      print >>output_file, ""

   ################################################################################################
   #### WRITE THE VARIABLES FOR THE MASTER MODEL AND ALL SCENARIO MODELS ##########################
   ################################################################################################

   # write the variables for the master binding instance, and then for each scenario.
   print >>output_file, "bounds"
   print >>output_file, ""
   
   problem_writer._output_objectives = False
   problem_writer._output_constraints = False
   problem_writer._output_variables = True

   # first step: write variable bounds

   problem_writer._output_continuous_variables = True
   problem_writer._output_integer_variables = False
   problem_writer._output_binary_variables = False

   print >>output_file, "\\ Begin variable bounds block for master"
   problem_writer._print_model_LP(master_binding_instance, output_file)
   print >>output_file, "\\ End variable bounds block for master"
   print >>output_file, ""

   for scenario_name in instances.keys():
      instance = instances[scenario_name]
      print >>output_file, "\\ Begin variable bounds block for scenario",scenario_name 
      problem_writer._print_model_LP(instance, output_file)
      print >>output_file, "\\ End variable bounds block for scenario",scenario_name
      print >>output_file, ""

   # second step: write integer indicators.

   problem_writer._output_continuous_variables = False
   problem_writer._output_integer_variables = True

   if integers_present(master_binding_instance, instances) is True:

      print >>output_file, "integer"
      print >>output_file, ""

      print >>output_file, "\\ Begin integer variable block for master"
      problem_writer._print_model_LP(master_binding_instance, output_file)
      print >>output_file, "\\ End integer variable block for master"
      print >>output_file, ""
   
      for scenario_name in instances.keys():
         instance = instances[scenario_name]
         print >>output_file, "\\ Begin integer variable block for scenario",scenario_name 
         problem_writer._print_model_LP(instance, output_file)
         print >>output_file, "\\ End integer variable block for scenario",scenario_name
         print >>output_file, ""

   # third step: write binary indicators.

   problem_writer._output_integer_variables = False
   problem_writer._output_binary_variables = True

   if binaries_present(master_binding_instance, instances) is True:

      print >>output_file, "binary"
      print >>output_file, ""

      print >>output_file, "\\ Begin binary variable block for master"
      problem_writer._print_model_LP(master_binding_instance, output_file)
      print >>output_file, "\\ End binary variable block for master"
      print >>output_file, ""
   
      for scenario_name in instances.keys():
         instance = instances[scenario_name]
         print >>output_file, "\\ Begin binary variable block for scenario",scenario_name 
         problem_writer._print_model_LP(instance, output_file)
         print >>output_file, "\\ End integer binary block for scenario",scenario_name
         print >>output_file, ""

   # wrap up.
   print >>output_file, "end"

   # clean up.
   output_file.close()

   print ""
   print "Output file written to file=",output_filename

   print ""
   print "Done..."

   end_time = time.time()

   print ""
   print "Total execution time=%8.2f seconds" %(end_time - start_time)
   print ""

def write_ef(scenario_tree, instances, output_filename):

   start_time = time.time()

   ################################################################################################
   #### CREATE THE MASTER / BINDING INSTANCE ######################################################
   ################################################################################################

   master_binding_instance = Model()
   master_binding_instance.name = "MASTER"

   # walk the scenario tree - create variables representing the common values for all scenarios
   # associated with that node. the constraints will be created later. also create expected-cost
   # variables for each node, to be computed via constraints/objectives defined in a subsequent pass.
   # master variables are created for all nodes but those in the last stage. expected cost variables
   # are, for no particularly good reason other than easy coding, created for nodes in all stages.
   print "Creating variables for master binding instance"

   for stage in scenario_tree._stages:

      for (stage_variable, index_template, stage_variable_indices) in stage._variables:

         print "Creating master variable and blending constraints for decision variable=", stage_variable, ", indices=", index_template

         for tree_node in stage._tree_nodes:

            if stage != scenario_tree._stages[-1]:      

               master_variable_name = tree_node._name + "_" + stage_variable.name

               # because there may be a single stage variable and multiple indices, check
               # for the existence of the variable at this node - if you don't, you'll
               # inadvertently over-write what was there previously!
               master_variable = None
               try:
                  master_variable = getattr(master_binding_instance, master_variable_name)
               except:
                  # the deepcopy is probably too expensive (and unnecessary) computationally -
                  # easier to just use the constructor with the stage variable index/bounds/etc.
                  # NOTE: need to re-assign the master variables for each _varval - they probably
                  #       point to a bogus model.
                  new_master_variable = copy.deepcopy(stage_variable)
                  new_master_variable.name = master_variable_name
                  new_master_variable._model = master_binding_instance
                  setattr(master_binding_instance, master_variable_name, new_master_variable)

                  master_variable = new_master_variable

               for index in stage_variable_indices:

                  is_used = True # until proven otherwise                     
                  for scenario in tree_node._scenarios:
                     instance = instances[scenario._name]
                     if getattr(instance,stage_variable.name)[index].status == VarStatus.unused:
                        is_used = False

                  is_fixed = False # until proven otherwise
                  for scenario in tree_node._scenarios:
                     instance = instances[scenario._name]
                     if getattr(instance,stage_variable.name)[index].fixed is True:
                        is_fixed = True

                  if (is_used is True) and (is_fixed is False):
                           
                     # the following is necessary, specifically to get the name - deepcopy won't reset these attributes.
                     # and because presolve/simplification is name-based, the names *have* to be different.
                     master_variable[index].var = master_variable
                     master_variable[index].name = tree_node._name + "_" + master_variable[index].name

                     for scenario in tree_node._scenarios:

                        scenario_instance = instances[scenario._name]
                        scenario_variable = getattr(scenario_instance, stage_variable.name)
                        new_constraint_name = scenario._name + "_" + master_variable_name + "_" + str(index)
                        new_constraint = Constraint(name=new_constraint_name)
                        new_expr = master_variable[index] - scenario_variable[index]
                        new_constraint.add(None, (0.0, new_expr, 0.0))
                        new_constraint._model = master_binding_instance
                        setattr(master_binding_instance, new_constraint_name, new_constraint)

            # create a variable to represent the expected cost at this node -
            # the constraint to compute this comes later.
            expected_cost_variable_name = "EXPECTED_COST_" + tree_node._name
            expected_cost_variable = Var(name=expected_cost_variable_name)
            expected_cost_variable._model = master_binding_instance
            setattr(master_binding_instance, expected_cost_variable_name, expected_cost_variable)

   master_binding_instance.presolve()

   # ditto above for the (non-expected) cost variable.
   for stage in scenario_tree._stages:

      (cost_variable,cost_variable_index) = stage._cost_variable

      print "Creating master variable and blending constraints for cost variable=", cost_variable, ", index=", cost_variable_index      

      for tree_node in stage._tree_nodes:

         new_cost_variable_name = tree_node._name + "_" + cost_variable.name

         # TBD - the following is bad - check to see if it's already there (I suspect some of them are!!!)

         # this is undoubtedly wasteful, in that a cost variable
         # for each tree node is created with *all* indices. 
         new_cost_variable = copy.deepcopy(cost_variable)
         new_cost_variable.name = new_cost_variable_name
         new_cost_variable._model = master_binding_instance
         setattr(master_binding_instance, new_cost_variable_name, new_cost_variable)

         # the following is necessary, specifically to get the name - deepcopy won't reset these attributes.
         new_cost_variable[cost_variable_index].var = new_cost_variable
         if cost_variable_index is not None:
            # if the variable index is None, the variable is derived from a VarValue, so the
            # name gets updated automagically.
            new_cost_variable[cost_variable_index].name = tree_node._name + "_" + new_cost_variable[cost_variable_index].name

         for scenario in tree_node._scenarios:

            scenario_instance = instances[scenario._name]
            scenario_cost_variable = getattr(scenario_instance, cost_variable.name)
            new_constraint_name = scenario._name + "_" + new_cost_variable_name + "_" + str(cost_variable_index)
            new_constraint = Constraint(name=new_constraint_name)
            new_expr = new_cost_variable[cost_variable_index] - scenario_cost_variable[cost_variable_index]
            new_constraint.add(None, (0.0, new_expr, 0.0))
            new_constraint._model = master_binding_instance
            setattr(master_binding_instance, new_constraint_name, new_constraint)

   # create the constraints for computing the master per-node cost variables,
   # i.e., the current node cost and the expected cost of the child nodes.
   # if the root, then the constraint is just the objective.

   for stage in scenario_tree._stages:

      (stage_cost_variable,stage_cost_variable_index) = stage._cost_variable

      for tree_node in stage._tree_nodes:

         node_expected_cost_variable_name = "EXPECTED_COST_" + tree_node._name
         node_expected_cost_variable = getattr(master_binding_instance, node_expected_cost_variable_name)

         node_cost_variable_name = tree_node._name + "_" + stage_cost_variable.name
         node_cost_variable = getattr(master_binding_instance, node_cost_variable_name)                        
            
         constraint_expr = node_expected_cost_variable - node_cost_variable[stage_cost_variable_index]

         for child_node in tree_node._children:

            child_node_expected_cost_variable_name = "EXPECTED_COST_" + child_node._name
            child_node_expected_cost_variable = getattr(master_binding_instance, child_node_expected_cost_variable_name)
            constraint_expr = constraint_expr - (child_node._conditional_probability * child_node_expected_cost_variable)

         new_constraint_name = "COST" + "_" + node_cost_variable_name + "_" + str(cost_variable_index)
         new_constraint = Constraint(name=new_constraint_name)
         new_constraint.add(None, (0.0, constraint_expr, 0.0))
         new_constraint._model = master_binding_instance                     
         setattr(master_binding_instance, new_constraint_name, new_constraint)

         if tree_node._parent is None:

            an_instance = instances[instances.keys()[0]]
            an_objective = an_instance.active_components(Objective)
            opt_sense = an_objective[an_objective.keys()[0]].sense

            new_objective = Objective(name="MASTER", sense=opt_sense)
            new_objective._data[None].expr = node_expected_cost_variable
            setattr(master_binding_instance, "MASTER", new_objective)

   master_binding_instance.presolve()

   ################################################################################################
   #### WRITE THE COMPOSITE MODEL #################################################################
   ################################################################################################

   print ""
   print "Starting to write extensive form"

   # create the output file.
   problem_writer = cpxlp.ProblemWriter_cpxlp()
   output_file = open(output_filename,"w")

   problem_writer._output_prefixes = True # we always want prefixes

   ################################################################################################
   #### WRITE THE MASTER OBJECTIVE ################################################################
   ################################################################################################

   # write the objective for the master binding instance.
   problem_writer._output_objectives = True
   problem_writer._output_constraints = False
   problem_writer._output_variables = False

   print >>output_file, "\\ Begin objective block for master"
   problem_writer._print_model_LP(master_binding_instance, output_file)
   print >>output_file, "\\ End objective block for master"
   print >>output_file, ""

   ################################################################################################
   #### WRITE THE CONSTRAINTS FOR THE MASTER MODEL AND ALL SCENARIO MODELS ########################
   ################################################################################################

   print >>output_file, "s.t."
   print >>output_file, ""
   
   problem_writer._output_objectives = False
   problem_writer._output_constraints = True
   problem_writer._output_variables = False

   print >>output_file, "\\ Begin constraint block for master"
   problem_writer._print_model_LP(master_binding_instance, output_file)
   print >>output_file, "\\ End constraint block for master",
   print >>output_file, ""

   for scenario_name in instances.keys():
      instance = instances[scenario_name]
      print >>output_file, "\\ Begin constraint block for scenario",scenario_name       
      problem_writer._print_model_LP(instance, output_file)
      print >>output_file, "\\ End constraint block for scenario",scenario_name
      print >>output_file, ""

   ################################################################################################
   #### WRITE THE VARIABLES FOR THE MASTER MODEL AND ALL SCENARIO MODELS ##########################
   ################################################################################################

   # write the variables for the master binding instance, and then for each scenario.
   print >>output_file, "bounds"
   print >>output_file, ""
   
   problem_writer._output_objectives = False
   problem_writer._output_constraints = False
   problem_writer._output_variables = True

   # first step: write variable bounds

   problem_writer._output_continuous_variables = True
   problem_writer._output_integer_variables = False
   problem_writer._output_binary_variables = False

   print >>output_file, "\\ Begin variable bounds block for master"
   problem_writer._print_model_LP(master_binding_instance, output_file)
   print >>output_file, "\\ End variable bounds block for master"
   print >>output_file, ""
   
   for scenario_name in instances.keys():
      instance = instances[scenario_name]
      print >>output_file, "\\ Begin variable bounds block for scenario",scenario_name 
      problem_writer._print_model_LP(instance, output_file)
      print >>output_file, "\\ End variable bounds block for scenario",scenario_name
      print >>output_file, ""

   # second step: write integer indicators.

   problem_writer._output_continuous_variables = False
   problem_writer._output_integer_variables = True

   if integers_present(master_binding_instance, instances) is True:

      print >>output_file, "integer"
      print >>output_file, ""

      print >>output_file, "\\ Begin integer variable block for master"
      problem_writer._print_model_LP(master_binding_instance, output_file)
      print >>output_file, "\\ End integer variable block for master"
      print >>output_file, ""
   
      for scenario_name in instances.keys():
         instance = instances[scenario_name]
         print >>output_file, "\\ Begin integer variable block for scenario",scenario_name 
         problem_writer._print_model_LP(instance, output_file)
         print >>output_file, "\\ End integer variable block for scenario",scenario_name
         print >>output_file, ""

   # third step: write binary indicators.

   problem_writer._output_integer_variables = False
   problem_writer._output_binary_variables = True

   if binaries_present(master_binding_instance, instances) is True:

      print >>output_file, "binary"
      print >>output_file, ""

      print >>output_file, "\\ Begin binary variable block for master"
      problem_writer._print_model_LP(master_binding_instance, output_file)
      print >>output_file, "\\ End binary variable block for master"
      print >>output_file, ""
   
      for scenario_name in instances.keys():
         instance = instances[scenario_name]
         print >>output_file, "\\ Begin binary variable block for scenario",scenario_name 
         problem_writer._print_model_LP(instance, output_file)
         print >>output_file, "\\ End integer binary block for scenario",scenario_name
         print >>output_file, ""

   # wrap up.
   print >>output_file, "end"

   # clean up.
   output_file.close()

   print ""
   print "Output file written to file=",output_filename

   print ""
   print "Done..."

   end_time = time.time()

   print ""
   print "Total execution time=%8.2f seconds" %(end_time - start_time)
   print ""   
