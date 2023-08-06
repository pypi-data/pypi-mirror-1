Scenario Tree Data Builder for the Stochastic Forestry Planning Problem
version 0.1

Files:
	build.py	:	Python script for making the data
	NodeStage1.dat	:	RootNode instance information
	StageVariables	:	Needed by build.py to completely build ScenarioStructure.dat
	ReferenceModel.dat	:	Needed by pysp to build the model


Usage:
	Two uncertainties are handled Price&Demand and Yield.
	An uncertainty is handled by selecting how many branches you want at each Stage (line 92 of build.py) and by selecting wich distribution you want to use (line 107 and 108)

	Then just run the script and the files appear in the same directory.
	Copy them (NodeStage*, ReferenceModel.dat and ScenarioStructure.dat) wherever you want and runph

	Remember not to delete/move NodeStage1.dat and ReferenceModel.dat