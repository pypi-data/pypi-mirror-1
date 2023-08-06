#!/usr/bin/env/python
""" Setup script for PuLP added by Stuart Mitchell 2007
Copyright 2007 Stuart Mitchell
"""
from distutils.core import setup

setup(name="pulp-or",
      version="1.3.03",
      description="""
      PuLP is an LP modeler written in python. PuLP can generate MPS or LP files
      and call GLPK[1], COIN CLP/CBC[2], CPLEX[3] and XPRESS[4] to solve linear
      problems.
      """,
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
