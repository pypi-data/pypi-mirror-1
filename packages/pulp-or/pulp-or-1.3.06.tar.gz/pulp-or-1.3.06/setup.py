#!/usr/bin/env/python
""" Setup script for PuLP added by Stuart Mitchell 2007
Copyright 2007 Stuart Mitchell
"""
from distutils.core import setup

setup(name="pulp-or",
      version="1.3.06",
      description="""
      PuLP is an LP modeler written in python. PuLP can generate MPS or LP files
      and call GLPK[1], COIN CLP/CBC[2], CPLEX[3] and XPRESS[4] to solve linear
      problems.
      """,
      long_description = """
A comprehensive wiki can be found at http://pulp-or.googlecode.com/

Use LpVariable() to create new variables. To create a variable 0 <= x <= 3
>>> x = LpVariable("x", 0, 3)

To create a variable 0 <= y <= 1
>>> y = LpVariable("y", 0, 1)

Use LpProblem() to create new problems. Create "myProblem"
>>> prob = LpProblem("myProblem", LpMinimize)

Combine variables to create expressions and constraints and add them to the
problem. 
>>> prob += x + y <= 2

If you add an expression (not a constraint), it will
become the objective.
>>> prob += -4*x + y

Choose a solver and solve the problem. ex:
>>> status = prob.solve(GLPK(msg = 0))

Display the status of the solution
>>> LpStatus[status]
'Optimal'

You can get the value of the variables using value(). ex:
>>> value(x)
2.0

Exported Classes:
    - LpProblem -- Container class for a Linear programming problem
    - LpVariable -- Variables that are added to constraints in the LP
    - LpConstraint -- A constraint of the general form 
      a1x1+a2x2 ...anxn (<=, =, >=) b 
    - LpConstraintVar -- Used to construct a column of the model in column-wise 
      modelling

Exported Functions:
    - value() -- Finds the value of a variable or expression
    - lpSum() -- given a list of the form [a1*x1, a2x2, ..., anxn] will construct 
      a linear expression to be used as a constraint or variable
    - lpDot() --given two lists of the form [a1, a2, ..., an] and 
      [ x1, x2, ..., xn] will construct a linear epression to be used 
      as a constraint or variable
""",
      keywords = ["Optimization", "Linear Programming", "Operations Research"],
      author="J.S. Roy and S.A. Mitchell",
      author_email="s.mitchell@auckland.ac.nz",
      url="http://pulp-or.googlecode.com/",
      #ext_modules = [pulpCOIN],
      py_modules=["pulp.pulp","pulp.sparse"],
      package_dir={'pulp':'pulp-or/src'},
      packages = ['pulp'],
      package_data = {'pulp' : ["AUTHORS","LICENSE","pulp.cfg.linux",
                                "pulp.cfg.win",
                                "CoinMP.dll","LICENSE.CoinMP.txt",
                                "AUTHORS.CoinMP.txt","README.CoinMP.txt",
                                "libCbc.so","libCbcSolver.so",
                                "libCgl.so", "libClp.so", "libCoinMP.so",
                                "libCoinUtils.so","libOsi.so",
                                "libOsiCbc.so", "libOsiClp.so"]}
      )
