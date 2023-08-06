Using Pyomo on the classic diet problem.
========================================

The goal of this problem is to minimize cost while ensuring that the diet meets nutritional requirements.


Solving with AMPL
-----------------

Files

  diet1.mod     - The AMPL model
  diet1.dat     - A simple data file for this example
  diet1.ampl    - An AMPL script to solve the diet1 problem
                  (This uses PICO, but other solvers could be used that
                  can read in AMPL *.nl files.)

Running AMPL

  1. Add the directory containing 'cplex' to your PATH environment
  2. ampl diet1.ampl



Solving with Pyomo
------------------

Files

  diet1.py      - A Python model written with Pyomo objects
  diet1.dat     - A simple data file for this example

Running Pyomo

  1. ../../../scripts/pyomo diet1.py diet1.dat

