"""Module containing routines for estimating covariance models.
"""

import math
from pyvol.tseries.Transforms import SeqXform
import CovUtils

class CovEstimator:
    """Base class illustrating the API covariance estimators should follow

    All covariance estimators should subclass this class and override at
    least the Estimate method.
    """

    def __init__(self):
        self.returnColName = None #Set later by SetReturnColName
        self.returnCol = None     #Set later by Startup

    def SetReturnColName(self, returnColName):
        """Set the return column name.
        
        INPUTS:
        
        -- returnColName:        String indicating which column to look at
                                 for lowest level return data.
        
        -------------------------------------------------------
        
        PURPOSE:        This method tells the estimator what column in
                        a Sequence.TimeSeq object will contain the lowest
                        level set of return data.
        
        """
        self.returnColName = returnColName

    def Startup(self, query):
        """Prepare to do estimation on data in a given query.
        
        INPUTS:
        
        -- query:        A Sequence.TimeSeq object with raw data for estimation.
        
        -------------------------------------------------------
        
        PURPOSE:        Prepare to do estimation on data in a given query.
                        Subclasses may override if desired.
        
        """
        self.returnCol = query.GetColIndex(self.returnColName)

    def Shutdown(self, query):
        """Finishing doing estimation on data in a given query.
        
        INPUTS:

        -- query:        A Sequence.TimeSeq object with raw data for estimation.
        
        -------------------------------------------------------
        
        PURPOSE:        Finish doing estimation on data in a given query.
                        Subclasses may override if desired.        
        
        """
        _ignore = self, query

    def Estimate(self, args, query, line):
        """Estimate volatility
        
        INPUTS:
        
        -- args:        Dictionary where keys are columns in query and values
                        are the values for the current line.
        
        -- query:       Full TimeSeq object containing past data that can
                        be used in doing the estimate.
        
        -- line:        Integer line number in query representing row we
                        are doing estimation for.
        
        -------------------------------------------------------
        
        RETURNS:        Return a floating point number representing an
                        estimate of the volatility for the next period.

                        This method should NOT modify query.
        
        -------------------------------------------------------
        
        PURPOSE:        Subclasses should override this method to produce
                        an estimate of the next period volatility.
        
        """
        raise NotImplementedError
                                        
class FixedLookackCovEstimator(CovEstimator):
    """Covariance estimator with a fixed lookback.
    """

    def __init__(self, lookback, *args, **kw):
        """Initializer.
        
        INPUTS:
        
        -- lookback:   Integer lookback to indicate how far back to look in
                       the data.
        
        -- *args, **kw:  Passed to CovEstimator.__init__.
        
        """
        self.lookback = lookback
        CovEstimator.__init__(self, *args, **kw)

    def Estimate(self, args, query, line):
        """Override Estimate as required by CovEstimator class

        Here is the function where we do the actual work. In this case,
        we simply look at the sample variance for data from self.lookback
        to the current line (not including current line).
        """
        
        _ignore = args
        c = self.returnCol
        startLine = line - self.lookback
        if (startLine < 0):
            return None
        returns = [row[c] for row in query.data[startLine:line]]
        volEst = math.sqrt(CovUtils.Var(returns))
        return volEst

class ThirteenWeekLookbackEstimator(FixedLookackCovEstimator):
    "Just like FixedLookackCovEstimator but with lookback of 13 weeks."

    def __init__(self, *args, **kw):
        FixedLookackCovEstimator.__init__(self, 13*5, *args, **kw)

class EstimateVols(SeqXform):
    """Transform to take an existing estimator and estimate vols.

    This transform is useful to simplify the process of computing estimates.

>>> import random
>>> import CovEst
>>> from pyvol.sims import DataSimulator, SimAPI
>>> seed = 64
>>> random.seed(seed)
>>> simulator = DataSimulator.PriceSimulator()
>>> returnColName = simulator.levelParams.retNames[-1]
>>> estimator = CovEst.FixedLookackCovEstimator(lookback=26*5)
>>> estimator.SetReturnColName(returnColName)
>>> estimatorTx = CovEst.EstimateVols(estimator, 'estimatedVol')
>>> query = simulator.MakeSimulatedData([estimatorTx])
>>> stats = SimAPI.MakeStats(query, simulator.levelParams)
>>> print stats
yearly    : ret = 0.026, vol = 0.195, sqCorrs = 1.000, 0.123, -0.084
quarterly : ret = 0.025, vol = 0.222, sqCorrs = 1.000, 0.103, 0.138
monthly   : ret = 0.026, vol = 0.223, sqCorrs = 1.000, 0.054, 0.158
weekly    : ret = 0.026, vol = 0.242, sqCorrs = 1.000, 0.175, 0.249
daily     : ret = 0.026, vol = 0.250, sqCorrs = 1.000, 0.422, 0.276

    """

    def __init__(self, estimator, estName):
        self.estimator = estimator
        SeqXform.__init__(self, [estimator.returnColName], [estName]) 

    def Startup(self, query):
        "Prepare to start doing estimation."
        self.estimator.Startup(query)

    def Shutdown(self, query):
        "Finish doing estimation."
        self.estimator.Shutdown(query)

    def ProcessRowInSeq(self, args, query, line):
        "Call our estimator and return results."
        volEst = self.estimator.Estimate(args, query, line)
        return [volEst]
        

class ScaleToConstantRisk(SeqXform):
    """Transform to scale positions to constant risk based on vol forecast.

    This class is useful in taking a target volatility level, existing
    positions, and forecast volatility and scaling the positions to have
    the given target volatility.
    """

    def __init__(self, targetVol, positionName, estimateName, scaledPos):
        """Initializer.
        
        INPUTS:
        
        -- targetVol:        Floating point target volatility.
        
        -- positionName:     String naming position field.   
        
        -- estimateName:     String naming vol estimate field.   
        
        -- scaledPos:        String naming output scaled position.
        """
        self.targetVol = targetVol
        SeqXform.__init__(self, [positionName, estimateName], [scaledPos])

    def ProcessRow(self, args):
        "Override as required by SeqXform to compute scaled position"
        
        position, estimate = [args[n] for n in self.inputFields]
        if (position is None or estimate is None):
            return [position]
        else:
            return [position / estimate * self.targetVol]

def _test():
    "Test docstrings in module."
    import doctest
    doctest.testmod()

if __name__ == "__main__":    
    _test()
    print 'Test finished.'
