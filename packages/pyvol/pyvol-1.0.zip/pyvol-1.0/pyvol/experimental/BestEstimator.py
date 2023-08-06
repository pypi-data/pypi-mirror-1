"""Module to produce the ''best estimator''.

This module provides the MakeEstimator function that returns an instance
of est.CovEst.CovEstimator deemed to be the ''best''. This is used by
other scripts to evaluate the best estimator.

You can have MakeEstimator return your estimator and then run other
scripts such as pyvol.sims.EvaluateBestEstimator.
"""
from pyvol.experimental import ExampleEstimators

def MakeEstimator():
    "Return best estimator."
    
    return ExampleEstimators.ExponentialCovEstimator(.99)
