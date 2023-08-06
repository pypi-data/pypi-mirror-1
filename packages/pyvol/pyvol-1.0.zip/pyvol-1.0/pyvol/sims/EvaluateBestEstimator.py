"""Module to select preferred estimator.

This is intended to be a simple script which evaluates what the user
has indicated as the best estimator in est.BestEstimator.MakeEstimator.
"""

import logging, sys
import Evaluator
from pyvol.experimental import BestEstimator

def Go(seed=64):
    """Function to evaluate best estimator
    
    INPUTS:
    
    -- seed=64:        Random seed to use for simulation.
    
    -------------------------------------------------------
    
    RETURNS:    Same as Evaluate.EvalEstimator plus estimator used.
    
    -------------------------------------------------------
    
    PURPOSE:    Evaluate the best estimator as indicated in
                BestEstimator.MakeEstimator.

    The following illustrates example usage:

>>> seed = 64 # random seed for simulations
>>> import EvaluateBestEstimator
>>> results = EvaluateBestEstimator.Go(seed=seed)
>>> import logging                                         # configure logging
>>> logging.addLevelName(logging.WARNING + 1, 'IMPORTANT') # so that test shows
>>> logging.getLogger('').setLevel(logging.WARNING + 1)    # up in log output
>>> logging.log(logging.WARNING + 1, '''
... Tested best estimator (%s) with seed=%s. Results:%c%s%c''' %
... (results[-1], seed, 10, results[0], 10))

    """
    estimator = BestEstimator.MakeEstimator()
    results = list(Evaluator.EvalEstimator(estimator, seed=seed))+[estimator]
    return results
    
if __name__ == '__main__':
    #If run as the main script, we simply run the evaulator
    logging.getLogger('').setLevel(logging.INFO)
    logging.info('Starting %s' % (sys.argv))
    if (len(sys.argv) == 1):
        userSeed = 64
    elif (len(sys.argv) == 2):
        userSeed = int(sys.argv[1])
    else:
        raise Exception('Invalid arguments. Usage:\n   %s [seed]\n' % (
            sys.argv[0]))
    userResults = Go(userSeed)
    print 'Estimator results:\n%s\n' % str(userResults[0])
