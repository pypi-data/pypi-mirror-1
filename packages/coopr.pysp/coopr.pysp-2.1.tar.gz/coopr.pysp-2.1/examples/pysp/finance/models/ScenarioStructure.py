# grab the pyomo modeling components.
from coopr.pyomo import *

model = Model()

# all set/parameter values are strings, representing the names of various entities/variables.

model.Stages = Set(ordered=True)
model.Nodes = Set()

model.NodeStage = Param(model.Nodes, within=model.Stages)
model.Children = Set(model.Nodes, within=model.Nodes, ordered=True)
model.ConditionalProbability = Param(model.Nodes)

model.Scenarios = Set(ordered=True)
model.ScenarioLeafNode = Param(model.Scenarios, within=model.Nodes)

model.StageVariables = Set(model.Stages)
model.StageCostVariable = Param(model.Stages)

# scenario data can be populated in one of two ways. the first is "scenario-based",
# in which a single .dat file contains all of the data for each scenario. the .dat
# file prefix must correspond to the scenario name. the second is "node-based",
# in which a single .dat file contains only the data for each node in the scenario
# tree. the node-based method is more compact, but the scenario-based method is
# often more natural when parameter data is generated via simulation. the default
# is scenario-based.
model.ScenarioBasedData = Param(within=Boolean, default=True)





