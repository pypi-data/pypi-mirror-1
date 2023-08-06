"""Module to read in all the doctests from source code that we want to test.

This module is designed so that "python setup.py test" can just look in
here and automatically suck in the other doctests from the source.
"""

import unittest, doctest
from pyvol.tseries import Sequence, Transforms
from pyvol.sims import (
    DataSimulator, Evaluator, EvaluateBestEstimator, MultiClusterSimulator)
from pyvol.est import (CovUtils, CovEst)
from pyvol.experimental import ExampleEstimators

def MakeMainDoctest():
    """Return a unittest.TestSuite object representing doctests from source code

>>> import unitTestsFromSrc
>>> t = unitTestsFromSrc.MakeMainDoctest()
>>> t.debug()
    """
    suite = unittest.TestSuite()

    for t in [Sequence, Transforms, MultiClusterSimulator, DataSimulator,
              Evaluator, ExampleEstimators, CovUtils, CovEst,
              EvaluateBestEstimator]:
        testCase = doctest.DocTestSuite(t)
        suite.addTest(testCase)

    return suite

mainTestSuite = MakeMainDoctest()
