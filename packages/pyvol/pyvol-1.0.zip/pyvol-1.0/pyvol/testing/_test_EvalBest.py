"""Module provides test_suite to test EvaluateBestEstimator.

This is useful in doing

  "python setup.py test -m pyvol.testing._test_EvalBest"

so that you can just see the results of the best estimator without
doing all the other tests.
"""

import unittest, doctest
from pyvol.sims import EvaluateBestEstimator

test_suite = unittest.TestSuite()
test_suite.addTest(doctest.DocTestSuite(EvaluateBestEstimator))
