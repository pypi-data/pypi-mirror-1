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

from phutils import *

class ScenarioTreeNode(object):

   """ Constructor

   """
   def __init__(self, *args, **kwds):

      self._name = ""
      self._stage = None
      self._parent = None
      self._children = [] # a collection of ScenarioTreeNodes
      self._conditional_probability = None # conditional on parent
      self._scenarios = [] # a collection of all Scenarios passing through this node in the tree

      # general use statistics for the variables at each node.
      # each attribute is a map between the variable name and a
      # parameter (over the same index set) encoding the corresponding
      # statistic computed over all scenarios for that node. the
      # parameters are named as the source variable name suffixed
      # by one of: "NODEMIN", "NODEAVG", and "NODEMAX". 
      # NOTE: the averages are probability_weighted - the min/max
      #       values are not.
      self._averages = {} 
      self._minimums = {}
      self._maximums = {}

   #
   # a utility to compute the cost of the current node plus the expected costs of child nodes.
   #
   def computeExpectedNodeCost(self, scenario_instance_map):

      # IMPT: This implicitly assumes convergence across the scenarios - if not, garbage results.
      instance = scenario_instance_map[self._scenarios[0]._name]
      my_cost = instance.active_components(Var)[self._stage._cost_variable[0].name][self._stage._cost_variable[1]]()
      child_cost = 0.0
      for child in self._children:
         child_cost += (child._conditional_probability * child.computeExpectedNodeCost(scenario_instance_map))
      return my_cost + child_cost


class Stage(object):

   """ Constructor

   """
   def __init__(self, *args, **kwds):
      self._name = ""
      self._tree_nodes = []      # a collection of ScenarioTreeNodes
      # a collection of pairs consisting of (1) references to pyomo model Vars, (2) the original match template string (for output purposes),
      # and (3) a *list* of the corresponding indices.
      # the variables are references to those objects belonging to the instance in the parent ScenarioTree.
      # NOTE: if the variable index is none, it is assumed that the entire variable is blended.
      self._variables = []
      # a tuple consisting of (1) a reference to a pyomo model Var that computes the stage-specific cost and (2) the corresponding index.
      # the index *is* the sole index in the cost variable, as the cost variable refers to a single variable index.
      self._cost_variable = (None, None)

class Scenario(object):

   """ Constructor

   """
   def __init__(self, *args, **kwds):
      self._name = None
      self._leaf_node = None  # allows for construction of node list
      self._node_list = []    # sequence from parent to leaf of ScenarioTreeNodes
      self._probability = 0.0 # the unconditional probability for this scenario, computed from the node list

class ScenarioTree(object):

   """ Constructor
       Arguments:
           model                         the (deterministic) model associated with this scenario tree
           nodes              (type-TBD) set of tree node IDs
           nodechildren       (type-TBD) map of node ID to a set of IDs indicating child nodes.
           nodestages         (type-TBD) map of tree node ID to stage ID
           nodeprobabilities  (type-TBD) map of node ID to corresponding conditional probability
           stages             (type-TBD) ordered set of stage IDs
           scenarios          (type-TBD) set of scenario node IDs
           scenarioleafs      (type-TBD) map of scenario ID to leaf tree node ID
           stagevariables     (type-TBD) map of stage ID to the names of the variables in the corresponding stage.
           stagecostvariables (type-TBD) map of stage ID to the name of the cost variable for the corresponding stage.
           nodedata           (type-TBD) map of node ID to the name of the corresponding data file (prefix only - no .dat suffix).
           scenariobaseddata  (type-TBD) parameter indicating whether instance data comes from scenario-based or node-based .dat files.
   """
   def __init__(self, *args, **kwds):
      self._name = None # TBD - some arbitrary identifier
      self._reference_instance = None # TBD - the reference (deterministic) base model

      # the core objects defining the scenario tree.
      self._tree_nodes = [] # collection of ScenarioTreeNodes
      self._stages = [] # collection of Stages - assumed to be in time-order. the set (provided by the user) itself *must* be ordered.
      self._scenarios = [] # collection of Scenarios

      # dictionaries for the above.
      self._tree_node_map = {}
      self._stage_map = {}
      self._scenario_map = {}

      # mapping of stages to sets of variables which belong in the corresponding stage.
      self._stage_variables = {}

      # a boolean indicating how data for scenario instances is specified.
      # possibly belongs elsewhere, e.g., in the PH algorithm.
      self._scenario_based_data = None

      # every stage has a cost variable - this is a variable/index pair.
      self._cost_variable = None

      # working copies based on the input arguments - only used
      # for constructing the tree, and subsequently discarded.
      node_ids = None
      node_child_ids = None
      node_stage_ids = None
      node_probability_map = None
      stage_ids = None
      stage_variable_ids = None
      stage_cost_variable_ids = None
      scenario_ids = None
      scenario_leaf_ids = None
      scenario_based_data = None

      # process the keyword options
      for key in kwds.keys():
         if key == "model":
            self._reference_instance = kwds[key]
         elif key == "nodes":
            node_ids = kwds[key]
         elif key == "nodechildren":
            node_child_ids = kwds[key]            
         elif key == "nodestages":
            node_stage_ids = kwds[key]
         elif key == "nodeprobabilities":
            node_probability_map = kwds[key]            
         elif key == "stages":
            stage_ids = kwds[key]
         elif key == "stagevariables":
            stage_variable_ids = kwds[key]
         elif key == "stagecostvariables":
            stage_cost_variable_ids = kwds[key]                                                            
         elif key == "scenarios":
            scenario_ids = kwds[key]
         elif key == "scenarioleafs":
            scenario_leaf_ids = kwds[key]
         elif key == "scenariobaseddata":
            scenario_based_data = kwds[key]            
         else:
            print "Unknown option=" + key + " specified in call to ScenarioTree constructor"

      # TBD - verify type of keyword arguments match expectation, and that they're all supplied.
      if self._reference_instance is None:
         raise ValueError, "A reference model must be supplied in the ScenarioTree constructor"         
      if node_ids is None:
         raise ValueError, "A set of node IDs must be supplied in the ScenarioTree constructor"
      if node_child_ids is None:
         raise ValueError, "A map from node IDs to the set of child node ID must be supplied in the ScenarioTree constructor"           
      if node_stage_ids is None:
         raise ValueError, "A map from node ID to stage ID must be supplied in the ScenarioTree constructor"
      if node_probability_map is None:
         raise ValueError, "A map from node ID to the corresponding conditional probability must be supplied in the ScenarioTree constructor"     
      if stage_ids is None:
         raise ValueError, "A set of stage IDs must be supplied in the ScenarioTree constructor"
      if stage_variable_ids is None:
         raise ValueError, "A map from stage ID to the corresponding set of variable names must be supplied in the ScenarioTree constructor"
      if stage_cost_variable_ids is None:
         raise ValueError, "A map from stage ID to the corresponding stage cost variable name must be supplied in the ScenarioTree constructor"                  
      if scenario_ids is None:
         raise ValueError, "A set of scenario IDs must be supplied in the Scenario Tree constructor"
      if scenario_leaf_ids is None:
         raise ValueError, "A map from scenario ID to the leaf tree node ID must be supplied in the ScenarioTree constructor"
      if scenario_leaf_ids is None:
         raise ValueError, "A map from scenario ID to the leaf tree node ID must be supplied in the ScenarioTree constructor"
      if scenario_based_data is None:
         raise ValueError, "A boolean indicating whether the instance data is obtained from per-scenario or per-node sources must be supplied in the ScenarioTree constructor"

      # save the method for instance data storage.
      self._scenario_based_data = scenario_based_data()

      # the input stages must be ordered, for both output purposes and knowledge of the final stage.
      if stage_ids.ordered is False:
         raise ValueError, "An ordered set of stage IDs must be supplied in the ScenarioTree constructor"

      #     
      # construct the actual tree objects
      #

      # construct the stage objects w/o any linkages first; link them up
      # with tree nodes after these have been fully constructed.
      for stage_name in stage_ids:
         new_stage = Stage()
         new_stage._name = stage_name
         self._stages.append(new_stage)
         self._stage_map[stage_name] = new_stage

      # construct the tree node objects themselves in a first pass,
      # and then link them up in a second pass to form the tree.
      # can't do a single pass because the objects may not exist.
      for tree_node_name in node_ids:
         new_tree_node = ScenarioTreeNode()
         new_tree_node._name = tree_node_name

         self._tree_nodes.append(new_tree_node)
         self._tree_node_map[tree_node_name] = new_tree_node

         new_tree_node._conditional_probability = node_probability_map[tree_node_name].value

         if tree_node_name not in node_stage_ids:
            raise ValueError, "No stage is assigned to tree node=" + tree_node._name
         else:
            stage_name = node_stage_ids[new_tree_node._name].value
            if stage_name not in self._stage_map.keys():
               raise ValueError, "Unknown stage=" + stage_name + " assigned to tree node=" + tree_node._name
            else:
               new_tree_node._stage = self._stage_map[stage_name]
               self._stage_map[stage_name]._tree_nodes.append(new_tree_node)

      # link up the tree nodes objects based on the child id sets.
      for this_node in self._tree_nodes:
         this_node._children = []
         if this_node._name in node_child_ids: # otherwise, you're at a leaf and all is well.
            child_ids = node_child_ids[this_node._name]
            for child_id in child_ids:
               if child_id in self._tree_node_map.keys():
                  child_node = self._tree_node_map[child_id]
                  this_node._children.append(self._tree_node_map[child_id])
                  if child_node._parent is None:
                     child_node._parent = this_node
                  else:
                     raise ValueError, "Multiple parents specified for tree node="+child_id+"; existing parent node="+child_node._parent._name+"; conflicting parent node="+this_node._name
               else:
                  raise ValueError, "Unknown child tree node=" + child_id + " specified for tree node=" + this_node._name

      # at this point, the scenario tree nodes and the stages are set - no
      # two-pass logic necessary when constructing scenarios.
      for scenario_name in scenario_ids:
         new_scenario = Scenario()
         new_scenario._name=scenario_name

         if scenario_name not in scenario_leaf_ids.keys():
            raise ValueError, "No leaf tree node specified for scenario=" + scenario_name
         else:
            scenario_leaf_node_name = scenario_leaf_ids[scenario_name].value
            if scenario_leaf_node_name not in self._tree_node_map.keys():
               raise ValueError, "Uknown tree node=" + scenario_leaf_node_name + " specified as leaf of scenario=" + scenario_name
            else:
               new_scenario._leaf_node = self._tree_node_map[scenario_leaf_node_name]

         current_node = new_scenario._leaf_node
         probability = 1.0
         while current_node is not None:
            new_scenario._node_list.append(current_node)
            current_node._scenarios.append(new_scenario) # links the scenarios to the nodes to enforce necessary non-anticipativity
            probability *= current_node._conditional_probability
            current_node = current_node._parent
         new_scenario._node_list.reverse()
         new_scenario._probability = probability

         self._scenarios.append(new_scenario)
         self._scenario_map[scenario_name] = new_scenario

      # map the variables to the stages - these are references, not copies.
      for stage_id in stage_variable_ids.keys():

         if stage_id not in self._stage_map.keys():
            raise ValueError, "Unknown stage=" + stage_id + " specified in scenario tree constructor (stage->variable map)"

         stage = self._stage_map[stage_id]
         variable_ids = stage_variable_ids[stage_id]

         for variable_string in variable_ids:

            if isVariableNameIndexed(variable_string) is True:

               variable_name, index_template = extractVariableNameAndIndex(variable_string)

               # validate that the variable exists and extract the reference.
               if variable_name not in self._reference_instance.active_components(Var):
                  raise ValueError, "Variable=" + variable_name + " associated with stage=" + stage_id + " is not present in model=" + self._reference_instance.name
               variable = self._reference_instance.active_components(Var)[variable_name]               

               # extract all "real", i.e., fully specified, indices matching the index template.
               match_indices = extractVariableIndices(variable, index_template)               

               # there is a possibility that no indices match the input template.
               # if so, let the user know about it.
               if len(match_indices) == 0:
                  raise RuntimeError, "No indices match template="+str(index_template)+" for variable="+variable_name+" ; encountered in scenario tree specification for model="+self._reference_instance.name
                  
               stage._variables.append((variable, index_template, match_indices))

            else:

               # verify that the variable exists.
               if variable_string not in self._reference_instance.active_components(Var).keys():
                  raise RuntimeError, "Unknown variable=" + variable_string + " associated with stage=" + stage_id + " is not present in model=" + self._reference_instance.name

               variable = self._reference_instance.active_components(Var)[variable_string]

               # 9/14/2009 - now forcing the user to explicit specify the full
               # match template (e.g., "foo[*,*]") instead of just the variable
               # name (e.g., "foo") to represent the set of all indices.
               
               # if the variable is a singleton - that is, non-indexed - no brackets is fine.
               # we'll just tag the var[None] variable value with the (suffix,value) pair.
               if None not in variable._index:
                  raise RuntimeError, "Variable="+variable_string+" is an indexed variable, and templates must specify an index match; encountered in scenario tree specification for model="+self._reference_instance.name                  

               match_indices = []
               match_indices.append(None)

               stage._variables.append((variable, "", match_indices))

      for stage_id in stage_cost_variable_ids.keys():

         if stage_id not in self._stage_map.keys():
            raise ValueError, "Unknown stage=" + stage_id + " specified in scenario tree constructor (stage->cost variable map)"
         stage = self._stage_map[stage_id]
         
         cost_variable_string = stage_cost_variable_ids[stage_id].value # de-reference is required to access the parameter value

         # to be extracted from the string.
         cost_variable_name = None
         cost_variable = None
         cost_variable_index = None

         # do the extraction.
         if isVariableNameIndexed(cost_variable_string) is True:

            cost_variable_name, index_template = extractVariableNameAndIndex(cost_variable_string)

            # validate that the variable exists and extract the reference.
            if cost_variable_name not in self._reference_instance.active_components(Var):
               raise ValueError, "Variable=" + cost_variable_name + " associated with stage=" + stage_id + " is not present in model=" + self._reference_instance.name
            cost_variable = self._reference_instance.active_components(Var)[cost_variable_name]               

            # extract all "real", i.e., fully specified, indices matching the index template.
            match_indices = extractVariableIndices(cost_variable, index_template)

            # only one index can be supplied for a stage cost variable.
            if len(match_indices) != 1:
               raise RuntimeError, "Only one index can be specified for a stage cost variable - "+str(len(match_indices))+"match template="+index_template+" for variable="+cost_variable_name+" ; encountered in scenario tree specification for model="+self._reference_instance.name

            cost_variable_index = match_indices[0]

         else:

            cost_variable_name = cost_variable_string

            # validate that the variable exists and extract the reference
            if cost_variable_name not in self._reference_instance.active_components(Var):
               raise ValueError, "Cost variable=" + cost_variable_name + " associated with stage=" + stage_id + " is not present in model=" + self._reference_instance.name
            cost_variable = self._reference_instance.active_components(Var)[cost_variable_name]
            
         # store the validated info.
         stage._cost_variable = (cost_variable, cost_variable_index)

      # for output purposes, it is useful to known the maximal length of identifiers
      # in the scenario tree for any particular category. I'm building these up
      # incrementally, as they are needed. 0 indicates unassigned.
      self._max_scenario_id_length = 0

      # does the actual traversal to populate the members.
      self.computeIdentifierMaxLengths()

   #
   # returns the root node of the scenario tree
   #
   def findRootNode(self):

      for tree_node in self._tree_nodes:
         if tree_node._parent is None:
            return tree_node
      return None

   #
   # a utility function to compute, based on the current scenario tree content,
   # the maximal length of identifiers in various categories.
   #
   def computeIdentifierMaxLengths(self):

      self._max_scenario_id_length = 0
      for scenario in self._scenarios:
         if len(scenario._name) > self._max_scenario_id_length:
            self._max_scenario_id_length = len(scenario._name)

   #
   # a utility function to (partially, at the moment) validate a scenario tree
   #
   def validate(self):

      # for any node, the sum of conditional probabilities of the children should sum to 1.
      for tree_node in self._tree_nodes:
         sum_probabilities = 0.0
         if len(tree_node._children) > 0:
            for child in tree_node._children:
               sum_probabilities += child._conditional_probability
            if abs(1.0 - sum_probabilities) > 0.000001:
               print "The child conditional probabilities for tree node=" + child._name + " sums to " + `sum_probabilities`
               return False

      # ensure that there is only one root node in the tree
      num_roots = 0
      root_ids = []
      for tree_node in self._tree_nodes:
         if tree_node._parent is None:
            num_roots += 1
            root_ids.append(tree_node._name)

      if num_roots != 1:
         print "Illegal set of root nodes detected: " + `root_ids`
         return False

      # there must be at least one scenario passing through each tree node.
      for tree_node in self._tree_nodes:
         if len(tree_node._scenarios) == 0:
            print "There are no scenarios associated with tree node=" + tree_node._name
            return False
      
      return True

   #
   # a utility function to pretty-print the static/non-cost information associated with a scenario tree
   #

   def pprint(self):

      print "Scenario Tree Detail"

      print "----------------------------------------------------"
      if self._reference_instance is not None:
         print "Model=" + self._reference_instance.name
      else:
         print "Model=" + "Unassigned"
      print "----------------------------------------------------"         
      print "Tree Nodes:"
      print ""
      for tree_node_name, tree_node in sorted(self._tree_node_map.iteritems()):
         print "\tName=" + tree_node_name
         if tree_node._stage is not None:
            print "\tStage=" + tree_node._stage._name
         else:
            print "\t Stage=None"
         if tree_node._parent is not None:
            print "\tParent=" + tree_node._parent._name
         else:
            print "\tParent=" + "None"
         if tree_node._conditional_probability is not None:
            print "\tConditional probability=%4.4f" % tree_node._conditional_probability
         else:
            print "\tConditional probability=" + "***Undefined***"
         print "\tChildren:"
         if len(tree_node._children) > 0:
            for child_node in sorted(tree_node._children):
               print "\t\t" + child_node._name
         else:
            print "\t\tNone"
         print "\tScenarios:"
         if len(tree_node._scenarios) == 0:
            print "\t\tNone"
         else:
            for scenario in tree_node._scenarios:
               print "\t\t" + scenario._name
         print ""
      print "----------------------------------------------------"
      print "Stages:"
      for stage_name, stage in sorted(self._stage_map.iteritems()):
         print "\tName=" + stage_name
         print "\tTree Nodes: "
         for tree_node in stage._tree_nodes:
            print "\t\t" + tree_node._name
         print "\tVariables: "
         for (variable, index_template, indices) in stage._variables:
            if (len(indices) == 1) and (indices[0] == None):
               print "\t\t" + variable.name
            else:
               print "\t\t",variable.name,":",index_template
         print "\tCost Variable: "            
         if stage._cost_variable[1] is None:
            print "\t\t" + stage._cost_variable[0].name
         else:
            print "\t\t" + stage._cost_variable[0].name + indexToString(stage._cost_variable[1])
         print ""            
      print "----------------------------------------------------"
      print "Scenarios:"
      for scenario_name, scenario in sorted(self._scenario_map.iteritems()):
         print "\tName=" + scenario_name
         print "\tProbability=%4.4f" % scenario._probability
         if scenario._leaf_node is None:
            print "\tLeaf node=None"
         else:
            print "\tLeaf node=" + scenario._leaf_node._name
         print "\tTree node sequence:"
         for tree_node in scenario._node_list:
            print "\t\t" + tree_node._name
         print ""                        
      print "----------------------------------------------------"

   #
   # a utility function to pretty-print the cost information associated with a scenario tree
   #

   def pprintCosts(self, scenario_instance_map):

      print "Scenario Tree Costs"
      print "***WARNING***: Assumes full (or nearly so) convergence of scenario solutions at each node in the scenario tree - computed costs are invalid otherwise"

      print "----------------------------------------------------"
      if self._reference_instance is not None:
         print "Model=" + self._reference_instance.name
      else:
         print "Model=" + "Unassigned"

      print "----------------------------------------------------"      
      print "Tree Nodes:"
      print ""
      for tree_node_name, tree_node in sorted(self._tree_node_map.iteritems()):
         print "\tName=" + tree_node_name
         if tree_node._stage is not None:
            print "\tStage=" + tree_node._stage._name
         else:
            print "\t Stage=None"
         if tree_node._parent is not None:
            print "\tParent=" + tree_node._parent._name
         else:
            print "\tParent=" + "None"
         if tree_node._conditional_probability is not None:
            print "\tConditional probability=%4.4f" % tree_node._conditional_probability
         else:
            print "\tConditional probability=" + "***Undefined***"
         print "\tChildren:"
         if len(tree_node._children) > 0:
            for child_node in sorted(tree_node._children):
               print "\t\t" + child_node._name
         else:
            print "\t\tNone"
         print "\tScenarios:"
         if len(tree_node._scenarios) == 0:
            print "\t\tNone"
         else:
            for scenario in tree_node._scenarios:
               print "\t\t" + scenario._name
         print "\tExpected node cost=%10.4f" % tree_node.computeExpectedNodeCost(scenario_instance_map)
         print ""

      print "----------------------------------------------------"
      print "Scenarios:"
      print ""
      for scenario_name, scenario in sorted(self._scenario_map.iteritems()):
         instance = scenario_instance_map[scenario_name]

         print "\tName=" + scenario_name
         print "\tProbability=%4.4f" % scenario._probability

         if scenario._leaf_node is None:
            print "\tLeaf Node=None"
         else:
            print "\tLeaf Node=" + scenario._leaf_node._name

         print "\tTree node sequence:"
         for tree_node in scenario._node_list:
            print "\t\t" + tree_node._name

         aggregate_cost = 0.0
         for stage in self._stages:
            instance_cost_variable = instance.active_components(Var)[stage._cost_variable[0].name][stage._cost_variable[1]]()
            print "\tStage=%20s     Cost=%10.4f" % (stage._name, instance_cost_variable)
            aggregate_cost += instance_cost_variable
         print "\tTotal scenario cost=%10.4f" % aggregate_cost
         print ""
      print "----------------------------------------------------"      
