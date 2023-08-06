###########################################################################################
10-scenario instances 
###########################################################################################

CPLEX 10.1 EF values after 2 days of CPU time (values reported in CMS paper):

1ef10   152701.58 (1.32% optimality gap) - proved optimal by CPLEX 12.1 (16 threads, 3200 seconds real wall-clock time).
2ef10   148531.92 (1.54% optimality gap)
3ef10   148781.07 (1.13% optimality gap)
4ef10   159805.00 (2.15% optimality gap)
5ef10   153352.16 (1.68% optimality gap)

Using CPLEX 11.2 and PH - command-line: 

No fixing of continuous variables at the moment, as the resulting EF MIP is solvable.
Slamming after iteration 100, but not really - we haven't defined variable slam priorities. Cycle breaking when length exceeds 30.

runph --model-directory=models --instance-directory=XXXX --verbose --max-iterations=100 --rho-cfgfile=config/rhosetter1.0.cfg --enable-ww-extensions --ww-extension-cfgfile=config/XXX.cfg --solve-ef 

Immediately fixing results (with wwph-immediatefixing.cfg).

1ef10: Converges in 17 iterations. Post-EF objective=155475
2ef10: Converges in 8 iterations.  Post-EF objective=149743.78
3ef10: Converges in 26 iterations. Post-EF objective=151536.34
4ef10: Converges in 12 iterations. Post-EF objective=162803.48
5ef10: Converges in 15 iterations. Post-EF objective=153279.42

Fix lag = 10 (with wwph-fixlag10.cfg).

1ef10: Converges in 58 iterations. After solving remaining EF, objective=153119.72
2ef10: Converges in 44 iterations. After solving remaining EF, objective=149048.82
3ef10: Converges in 32 iterations. After solving remaining EF, objective=149973.9
4ef10: Converges in 85 iterations. After solving remaining EF, objective=161147.9 - exhibits a lot of cycle-breaking.
5ef10: Converges in 51 iterations. After solving remaining EF, objective=153279.42

Fix lag = 20 (with wwph-fixlag20.cfg).

1ef10: Converges in 64 iterations.  After solving remaining EF, objective=153542.68
2ef10: Converges in 110 iterations. After solving remaining EF, objective=149048.82
3ef10: Converges in 67 iterations.  After solving remaining EF, objective=149973.9
4ef10: ***FAILS TO CONVERGE - SLAMMING PRIORITIES ARE REQUIRED.
5ef10: Converges in 81 iterations.  After solving remaining EF, objective=153279.42

When linearizing the quadratic penalty term, add the following options to the command line:

--bounds-cfgfile=config/xboundsetter.cfg --linearize-nonbinary-penalty-terms=2

###########################################################################################
50-scenario instances 
###########################################################################################

Running CPLEX 12.1, 16 threads: 

1ef50 
2ef50 
3ef50 
4ef50 
5ef50 
