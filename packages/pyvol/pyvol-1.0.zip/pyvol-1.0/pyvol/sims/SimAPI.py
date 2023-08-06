"""Module providing an API for creating data simulators.
"""

import math, datetime
from pyvol.est.CovUtils import Mean

class SimAPI:
    """Provides an interface for data simulators to follow.

    This is a simple application programming interface (API) that data
    simulators should follow. Having a consistent interface for simulators
    makes it easier to try out different models.

    For an example, see MultiClusterSimulator.py
    """

    def __init__(self, startDate=datetime.date(1950, 1, 2),
                 endDate=datetime.date(2009, 1, 5)):
        """Initializer.
        
        INPUTS:
        
        -- startDate:        A datetime.date representing when the simulation
                             should start.   
        
        -- endDate:          A datetime.date representing when the simulation
                             should end.   
        
        """
        if (startDate.weekday() > 5):
            raise TypeError('startDate (%s) must be a weekday' % startDate)
        if (endDate.weekday() > 5):
            raise TypeError('endDate (%s) must be a weekday' % endDate)
        self.startDate = startDate
        self.endDate = endDate

    def MakeSimulatedData(self, preTxList=None):
        """Create a TimeSeq repreenting simulated data.
        
        INPUTS:
        
        -- preTxList=None:    Optional list of Transforms.SeqXform
                              instances to add when doing simulation.
                              These will be added BEFORE the computations
                              are done for the simulation on a given day
                              to ensure that things in preTxList never look
                              at the "future" data.
        
        -------------------------------------------------------
        
        RETURNS:        A TimeSeq instance with simulated data.
        
        -------------------------------------------------------
        
        PURPOSE:        This is the main method of the simulator. Sub-classes
                        should override this to produce a TimeSeq instance
                        containing the raw data for the simulation.
        """
        raise NotImplementedError

def MakeStats(query, levelParams):
    """Make string representing some summary statistics for returns.
    
    INPUTS:
    
    -- query:        TimeSeq with returns to analyze.
    
    -- levelParams:  Instance of MultilevelVolModelParams used to create query.
    
    -------------------------------------------------------

    RETURNS:    Return string showing summary info on returns and correlations.

    -------------------------------------------------------    
    
    PURPOSE:    Make statistics on returns and correlations in query.
    
    """
    result = []
    rets = [ExtractPeriodReturns(
        query, levelParams.levelFuncs[name], levelParams.retNames[num])
            for (num, name) in enumerate(levelParams.levelNames)]
    for num, name in enumerate(levelParams.levelNames):
        stats = ComputeStats(rets[num])
        mult = levelParams.multipliers[name]
        result.append(
            '%s: ret = %.3f, vol = %.3f, sqCorrs = %.3f, %.3f, %.3f' % ((
            name.ljust(10), stats[0]*mult, stats[1]*math.sqrt(mult)
            ) + tuple(stats[2][0:3])))
    return '\n'.join(result)

def ComputeStats(data):
    """Compute some summary statistics for given data.
    
    INPUTS:
    
    -- data:        List of numbers representing period returns.
    
    -------------------------------------------------------
    
    RETURNS:    The triple (avg, stdev, corrs) representing average,
                standard deviation, and auto-correlation coefficients
                of the input data.
    
    -------------------------------------------------------
    
    PURPOSE:    Compute summary stats for data.
    
    """
    avg = Mean(data)
    stdev = math.sqrt(Mean([(d-avg)**2 for d in data]))
    avgSq = Mean([d*d for d in data])
    stdevSq = math.sqrt(Mean([(d*d - avgSq)**2 for d in data]))
    corrs = [1]
    for i in range(1,5):
        cov = sum([(a*a-avgSq)*(b*b-avgSq)
                   for (a, b) in zip(data[0:-i],data[i:])]
                  ) / float(len(data) - i)
        corrs.append(cov/stdevSq/stdevSq)
    return avg, stdev, corrs

def ExtractPeriodReturns(query, periodFunc, valueCol, dateCol='event_date'):
    """Extract returns for a given period (e.g., daily, weekly, monthly).
    
    INPUTS:
    
    -- query:        TimeSeq containing raw data.
    
    -- periodFunc:   Function that takes a datetime.date and returns an
                     integer represting the period for that date. For example,
                     if you want to get yearly returns, this could be
                     GetYear, if you want quarterly returns, it could be
                     GetQuarter, etc.
    
    -- valueCol:     String name or integer index of column in query containing
                     the desired period returns.
    
    -- dateCol='event_date':        String name or integer index of column
                                    in query containing dates.
    
    -------------------------------------------------------
    
    RETURNS:    List of returns extracted from query.
    
    -------------------------------------------------------
    
    PURPOSE:    This funciton samples the query every time the periodFunc
                reports a differnt value for the date. This is useful for
                extracting returns over different periods.
    
    """
    if (isinstance(dateCol, (str, unicode))):
        dateCol = query.GetColIndex(dateCol)
    if (isinstance(valueCol, (str, unicode))):
        valueCol = query.GetColIndex(valueCol)
        
    result = []
    prevPeriod = None
    for line in query.data:
        date = line[dateCol]
        curPeriod = periodFunc(date)
        if (curPeriod != prevPeriod):
            result.append(line[valueCol])
        prevPeriod = curPeriod
        
    return result    
