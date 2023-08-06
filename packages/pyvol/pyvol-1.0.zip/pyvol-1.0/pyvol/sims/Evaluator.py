"""Contains functions to help evaulate estimator performance.
"""

import DataSimulator, SimAPI
from pyvol.est import CovEst, CovUtils
import math, random, logging

def EvaluateQuery(query, positionName, scaledPosName, estimateName,
                  returnColName, volColName, startDate,
                  targetVol=0.10 / math.sqrt(262)):
    """Evaluate peformance of a set of estimates on an existing query.
    
    INPUTS:
    
    -- query:        TimeSeq instances with positions, returns, and estimated
                     volatilities.
    
    -- positionName: String name of position column in query.       
    
    -- scaledPosName:  String name of new column with scaled positions which
                       will be added to query. 
    
    -- estimateName:   String name of field representing volatility estimates.
    
    -- returnColName:  String name of field representing each period returns.
    
    -- volColName:     String name of field representing true volatility for
                       each period. 
    
    -- startDate:      A datetime.date representing when to start the estimates.
    
    -- targetVol=0.10/math.sqrt(262):     Target volatility to scale to. For
                                          example, for data on week days we
                                          can set this to 0.10/math.sqrt(262)
                                          to indicate that the annualized
                                          volatility should be 10%.
    
    -------------------------------------------------------
    
    RETURNS:    The tuple (targError, spreadError, naiveSpreadError, perfErr)
                which represent:

                  targError :  The actual realized standard deviation minus
                               targetVol. This is a measure of the bias in
                               targetting a given volatility level.
                  spreadError: The mean of the squared return divided by
                               the realized vol minus 1. This gives a measure
                               of how the targetting error varies over the
                               sample.
                  naiveSprErr: The spreadError we would get if we just got
                               the target volatility right with a constant
                               scaling of the whole sample period.
                  perfErr:     The spreadError we would get if we new exactly
                               the underlying volatility at each sample. This
                               will not be zero becaue returns are still
                               random.
                               
    -------------------------------------------------------
    
    PURPOSE:    Evaluate performance of estimates in a query.
    
    """
    query.AddFields([CovEst.ScaleToConstantRisk(
        targetVol, positionName, estimateName, scaledPosName)])
    retCol = query.GetColIndex(returnColName)
    posCol = query.GetColIndex(positionName)
    sPosCol = query.GetColIndex(scaledPosName)
    volCol = query.GetColIndex(volColName)
    startLine = 0
    while (query.data[startLine][0] != startDate):
        startLine += 1
    qData = query.data[startLine:]
    unscaledReturns = [line[retCol] for line in qData]
    scaledReturns = [line[sPosCol]*line[retCol] for line in qData]
    perfectScaledReturns = [line[posCol]*line[retCol]/line[volCol]*targetVol
                            for line in qData]

    _junk, naiveSpreadError = ComputeEstimationError(
        unscaledReturns, targetVol)
    targError, spreadError = ComputeEstimationError(
        scaledReturns, targetVol)
    _junk, perfectSpreadError = ComputeEstimationError(
        perfectScaledReturns, targetVol)

    return targError, spreadError, naiveSpreadError, perfectSpreadError

def ComputeEstimationError(data, targetVol):
    """Compute error in estimating volatility.
    
    INPUTS:
    
    -- data:        List of returns for scaled positions.
    
    -- targetVol:   Target volatility the positions should have.     
    
    -------------------------------------------------------
    
    RETURNS:    The pair (targError, spreadError) representing 

                  targError :  The actual realized standard deviation minus
                               targetVol. This is a measure of the bias in
                               targetting a given volatility level.
                  spreadError: The mean of the squared return divided by
                               the realized vol minus 1. This gives a measure
                               of how the targetting error varies over the
                               sample.

    """
    stdev = math.sqrt(CovUtils.Var(data))
    targError = stdev - targetVol
    normalizedScaledReturns = [d/stdev for d in data]
    spreadError = CovUtils.Mean([(n*n - 1)**2 for n in normalizedScaledReturns])
    return targError, spreadError


def EvalEstimator(estimator, seed=64):
    """Evaluate the best estimator we currenlty have.
    
    INPUTS:

    -- estimator:      Instance of CovEstimator class to evaluate.  
    
    -- seed=64:        Random seed to make tests repeatable.
    
    -------------------------------------------------------
    
    RETURNS:    The tuple (query, targErr, spreadErr) represneting
                the full data for the simulation, the overal vol
                targettting error and the spread error.
    
    -------------------------------------------------------
    
    PURPOSE:    Evaluate the performance of a given estimator.

    -------------------------------------------------------

    RETURNS:    Tuple of the form (query, errors) where query is
                a TimeSeq object containing all the data for the trial
                and errors is a list containing the overall targetting error,
                spread error, naive error, and minimum possible error.

    -------------------------------------------------------

                The following illustrates example usage:

>>> import Evaluator
>>> from pyvol.est import CovEst
>>> estimtator = CovEst.FixedLookackCovEstimator(lookback=5*13)
>>> results = Evaluator.EvalEstimator(estimtator, seed=64)
>>> print results[0]
yearly    : ret = 0.026, vol = 0.195, sqCorrs = 1.000, 0.123, -0.084
quarterly : ret = 0.025, vol = 0.222, sqCorrs = 1.000, 0.103, 0.138
monthly   : ret = 0.026, vol = 0.223, sqCorrs = 1.000, 0.054, 0.158
weekly    : ret = 0.026, vol = 0.242, sqCorrs = 1.000, 0.175, 0.249
daily     : ret = 0.026, vol = 0.250, sqCorrs = 1.000, 0.422, 0.276
targErr= 0.00044, spreadErr= 4.05628, naiveError= 7.86425, minPossible=2.05384
    """
    random.seed(seed)
    
    logging.info('Producing simulation (seed = %s)' % (seed))
    simulator = DataSimulator.PriceSimulator()
    returnColName = simulator.levelParams.retNames[-1]    
    estimator.SetReturnColName(returnColName)
    estimatorTx = CovEst.EstimateVols(estimator, 'estimatedVol')
    query = simulator.MakeSimulatedData([estimatorTx])
    stats = SimAPI.MakeStats(query, simulator.levelParams)

    logging.info('Estimating vols')
    query.AddBlankColumns(['position'],default=1.0)

    logging.info('Evaluating performance')
    errors = EvaluateQuery(
        query, 'position', 'scaledPos', 'estimatedVol', returnColName,
        simulator.levelParams.annualizedVolNames[-1],
        query.data[260*3][0])

    stats += (
        '\ntargErr= %.5f, spreadErr= %.5f, naiveError= %.5f, minPossible=%.5f'%(
        errors))
    return stats, query, errors

def _test():
    "Test docstrings in module."
    import doctest
    doctest.testmod()

if __name__ == "__main__":    
    _test()
    print 'Test finished.'
