#
# This is the general multi-period deterministic version of the SIZES optimization model.
#

#
# Imports
#

import sys
import os
from os.path import abspath, dirname
sys.path.insert(0, dirname(dirname(dirname(dirname(abspath(__file__))))))
from coopr.pyomo import *

#
# Model
#

model = Model()

#
# Parameters
#

# the number of product sizes.
model.NumSizes = Param(within=NonNegativeIntegers)

# the set of sizes, labeled 1 through NumSizes.
def product_sizes_rule(model):
    return set(range(1, model.NumSizes()+1))    
model.ProductSizes = Set(initialize=product_sizes_rule)

# the number of stages and the corresponding set.
model.NumStages = Param(within=PositiveIntegers)

def stages_rule(model):
    ans = set()
    for i in range(1, model.NumStages+1):
        ans.add(i)
    return ans    

model.Stages = Set(initialize=stages_rule)

# the deterministic demands for product at each size.
model.Demands = Param(model.ProductSizes, model.Stages, within=NonNegativeReals)

# the unit production cost at each size.
model.UnitProductionCosts = Param(model.ProductSizes, within=NonNegativeReals)

# the setup cost for producing any units of size i.
model.SetupCosts = Param(model.ProductSizes, within=NonNegativeReals)

# the unit penalty cost of meeting demand for size j with larger size i.
model.UnitPenaltyCosts = Param(model.ProductSizes, within=NonNegativeReals)

# the cost to reduce a unit i to a lower unit j.
model.UnitReductionCost = Param(within=NonNegativeReals)

# a cap on the overall production within any time stage.
model.Capacity = Param(within=PositiveReals)

# TBD - should be able to define the "M" here, after the total demands are defined.

#
# Variables
#

# are any products at size i produced?
model.ProduceSize = Var(model.ProductSizes, model.Stages, domain=Boolean)

# the number of units at each size produced.
# TBD - the bounds should link/propagate through the domain, but they aren't.
model.NumProduced = Var(model.ProductSizes, model.Stages, domain=NonNegativeIntegers, bounds=(0.0, None))

# the number of units of size i cut (down) to meet demand for units of size j.
# TBD - currently the full matrix, need to figure out how to construct the tuples.
# TBD - the bounds should link/propagate through the domain, but they aren't.
# TBD - can actually be implicitly integer.
model.NumUnitsCut = Var(model.ProductSizes, model.ProductSizes, model.Stages, domain=NonNegativeIntegers, bounds=(0.0, None))

#
# Constraints
#

# ensure that demand is satisfied in each time stage.
def demand_satisfied_rule(i, t, model):
   expr = 0.0
   for j in model.ProductSizes:
      if j >= i:
         expr += model.NumUnitsCut[j,i,t]
   expr -= model.Demands[i,t]
   return (0.0, expr, None)

model.DemandSatisfied = Constraint(model.ProductSizes, model.Stages, rule=demand_satisfied_rule)

# ensure that you don't produce any units if the decision has been made to disable producion.
def enforce_production_rule(i, t, model):
   # TBD - compute M as the maximal demand
   M = 10000000
   expr = model.NumProduced[i, t] - M * model.ProduceSize[i, t]
   return (None, expr, 0.0)

model.EnforceProductionBinary = Constraint(model.ProductSizes, model.Stages, rule=enforce_production_rule)

# ensure that the production capacity is not exceeded for each time stage.
def enforce_capacity_rule(t, model):
   expr = 0.0
   for i in model.ProductSizes:
      expr += model.NumProduced[i,t]
   expr -= model.Capacity
   return (None, expr, 0.0)

model.EnforceCapacityLimit = Constraint(model.Stages, rule=enforce_capacity_rule)

# ensure that you can't generate inventory out of thin air.
def enforce_inventory_rule(i, t, model):
   expr = 0.0
   for tprime in model.Stages:
      if tprime <= t:
         for j in model.ProductSizes:
            if j <= i:
               expr += model.NumUnitsCut[i,j,tprime]
         expr -= model.NumProduced[i,tprime]
   return (None, expr, 0.0)

model.EnforceInventory = Constraint(model.ProductSizes, model.Stages, rule=enforce_inventory_rule)

#
# Objective
#

def total_cost_rule(model):
   ans = 0.0
   for t in model.Stages:
      for i in model.ProductSizes:
         ans = ans + (model.SetupCosts[i] * model.ProduceSize[i,t] + model.UnitProductionCosts[i] * model.NumProduced[i,t])

         # TBD - need to figure out the easier "i<j" syntax (assuming it exists).
         for j in model.ProductSizes:
            if j < i:
               ans = ans + model.UnitReductionCost * model.NumUnitsCut[i,j,t];
   return ans             

model.TotalCostObjective = Objective(rule = total_cost_rule, sense=minimize)
