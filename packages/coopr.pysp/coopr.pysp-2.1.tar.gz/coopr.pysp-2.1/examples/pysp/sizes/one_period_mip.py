#
# This is the one-period version of the SIZES optimization model.
#

#
# Imports
#

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

# the set of sizes.
def product_sizes_rule(model):
    return set(range(1, model.NumSizes()+1))    
model.ProductSizes = Set(initialize=product_sizes_rule)

# the deterministic demands for product at each size.
model.Demands = Param(model.ProductSizes, within=NonNegativeReals)

# the unit production cost at each size.
model.UnitProductionCosts = Param(model.ProductSizes, within=NonNegativeReals)

# the setup cost for producing any units of size i.
model.SetupCosts = Param(model.ProductSizes, within=NonNegativeReals)

# the unit penalty cost of meeting demand for size j with larger size i.
model.UnitPenaltyCosts = Param(model.ProductSizes, within=NonNegativeReals)

# the cost to reduce a unit i to a lower unit j.
model.UnitReductionCost = Param(within=NonNegativeReals)

# a derived set to constraint the NumUnitsCut variable domain.
# TBD: the (i,j) with i < j set should be a generic utility.
def num_units_cut_domain_rule(model):
   ans = set()
   for i in range(1,model.NumSizes+1):
      for j in range(1, i):
         ans.add((i,j))    
   return ans

model.NumUnitsCutDomain = Set(initialize=num_units_cut_domain_rule,dimen=2)

#
# Variables
#

# are any products at size i produced?
model.ProduceSize = Var(model.ProductSizes, domain=Boolean)

# the number of units at each size produced.
model.NumProduced = Var(model.ProductSizes, domain=NonNegativeReals)

# the number of units of size i cut (down) to meet demand for units of size j.
model.NumUnitsCut = Var(model.NumUnitsCutDomain, domain=NonNegativeReals)

# overall costs.
model.TotalCost = Var(domain=NonNegativeReals)

#
# Constraints
#

# compute the total number of units produced of size i, either natively or through "cutting" from a larger size.
def num_produced_rule(i, model):
   return (model.NumProduced[i] - model.Demands[i] + sum(model.NumUnitsCut[k,i] for k in range(i+1,model.NumSizes+1)) - sum(model.NumUnitsCut[i,l] for l in range(1,i))) == 0.0

model.NumProducedDefinition = Constraint(model.ProductSizes, rule=num_produced_rule)

# ensure that you don't produce any units if the decision has been made to disable producion.
def enforce_production_rule(i, model):
   # TBD - data-drive M
   return (None, model.NumProduced[i] - 1000000 * model.ProduceSize[i], 0.0)

model.EnforceProductionBinary = Constraint(model.ProductSizes, rule=enforce_production_rule)

# cost computation.
def total_cost_rule(model):
   production_costs = sum(model.SetupCosts[i] * model.ProduceSize[i] + model.UnitProductionCosts[i] * model.NumProduced[i] for i in model.ProductSizes)
   cut_costs = sum(model.UnitReductionCost * model.NumUnitsCut[i,j] for (i,j) in model.NumUnitsCutDomain if i != j)
   return (model.TotalCost - production_costs - cut_costs) == 0.0

model.ComputeTotalCost = Constraint(rule=total_cost_rule)

#
# Objective
#

def total_cost_rule(model):
    return model.TotalCost

model.TotalCostObjective = Objective(rule = total_cost_rule, sense=minimize)
