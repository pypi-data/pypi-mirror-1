models-nb: node-based reference scenario model
models-ab: arc-based reference scenario model
models-nb-yr: node-based reference scenario model with forest yield ratios

The scenario sub-problems - even at iteration 0 - take forever to solve to absolutely optimality. Consequently (and 
for a variety of other good reasons), the --enable-ww-extensions should be selected to provide a > 0 mipgap. 

A typical run is as follows:

../../../scripts/runph --model-directory=models-nb --instance-directory=chile-nodebased --max-iterations=20 --default-rho=1000 --rho-cfgfile=config/rhosetter.cfg --enable-ww-extensions --ww-extension-cfgfile=config/wwph.cfg --ww-extension-suffixfile=config/wwph.suffixes --verbose --write-ef --output-solver-logs

Best EF value for scenario=chile288-nb-yr: 5895098.9126 (3.8% gap - after 2 hours of CPLEX 11.2, 2 threads)
