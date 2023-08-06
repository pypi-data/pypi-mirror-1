"""This module provides the MultiClusterPriceSimulator.
"""

import datetime, math, random
from pyvol.tseries.Sequence import TimeSeq
from pyvol.tseries.Transforms import SeqXform
from pyvol.est.CovUtils import (
    GetYear, GetQuarter, GetMonth, GetWeek, GetDay)
import SimAPI

class MultilevelVolModelParams:
    """Class to hold parameters for multilevel volatility model.

    See __init__ for details of the model parameters.
    """

    def __init__(
        self,
        levelNames = ('yearly', 'quarterly', 'monthly', 'weekly', 'daily'),
        levelFuncs = (('yearly', GetYear), ('quarterly', GetQuarter),
                      ('monthly', GetMonth), ('weekly', GetWeek),
                      ('daily', GetDay)),
        alphas = (('yearly',.1), ('quarterly',.2), ('monthly',.25),
                  ('weekly',.3), ('daily', .3)),
        betas = (('yearly',.1), ('quarterly',.2), ('monthly',.2),
                  ('weekly',.3), ('daily', .3)),
        omegas = (('yearly',.1), ('quarterly',.5), ('monthly',.5),
                  ('weekly',.5), ('daily', .5)),
        multipliers = (('yearly', 1), ('quarterly', 4), ('monthly',12),
                       ('weekly', 52), ('daily', 260)),
        annualizedVolNames = None,
        retNames = None,
        ):
        """Initializer.
        
        INPUTS:
        
        -- levelNames=('yearly', 'quarterly', 'monthly', 'weekly', 'daily'):

                Sequence of names representing the different levels of the
                model from highest level to lowest level.
        
        -- levelFuncs: Dictionary where keys are levelNames and values are
                       functions which take a datetime.date and return an
                       integer representing that year, quarter, etc.
        
        -- alphas, betas, omegas:

                   Dictionaries where keys are levelNames and values are
                   the alpha parameters used in the model as described in
                   the class docstring.

        -- multipliers: Multipliers where keys are levelNames and values are
                        integers which say how many instances of that level
                        are in the bigest level. For example, this could be
                        something like

                   {'yearly' : 1, 'monthly' : 12, 'weekly' : 52}

                        if you just had three levels.
                   
        -- annualizedVolNames: List of names corresponding to levelNames
                               for how to name the annualized volatilites
                               for each level.
        
        -- retNames: List of names corresponding to levelNames for how
                     to name the returns for each level.   
        
        """

        if (annualizedVolNames is None):
            annualizedVolNames = [n + '_annVol' for n in levelNames]
        if (retNames is None):
            retNames = [n+'_ret' for n in levelNames]
            
        self.alphas = dict(alphas)
        self.betas = dict(betas)
        self.omegas = dict(omegas)
        self.levelNames = levelNames
        self.levelFuncs = dict(levelFuncs)
        self.multipliers = dict(multipliers)
        self.annualizedVolNames = annualizedVolNames
        self.retNames = retNames
        

class MultiClusterSimulator(SimAPI.SimAPI):

    """
>>> import datetime, random, math
>>> import MultiClusterSimulator
>>> random.seed(64) # for repeatability
>>> simulator = MultiClusterSimulator.MultiClusterSimulator()
>>> query = simulator.MakeSimulatedData()
>>> print MultiClusterSimulator.SimAPI.MakeStats(query, simulator.levelParams)
yearly    : ret = 0.026, vol = 0.195, sqCorrs = 1.000, 0.123, -0.084
quarterly : ret = 0.025, vol = 0.222, sqCorrs = 1.000, 0.103, 0.138
monthly   : ret = 0.026, vol = 0.223, sqCorrs = 1.000, 0.054, 0.158
weekly    : ret = 0.026, vol = 0.242, sqCorrs = 1.000, 0.175, 0.249
daily     : ret = 0.026, vol = 0.250, sqCorrs = 1.000, 0.422, 0.276
>>> 
    """


    def __init__(self, priceName='price', mean=0.065/260,
                 levelParams=None, **kw):
        """Initializer.
        
        INPUTS:

        -- priceName='price': Name of simulated price field to create.
        
        -- mean=0.065/260:   Mean log-return at lowest level of simulation.     
        
        -- levelParams=None: Instance of MultilevelVolModelParams. If None,
                             then we use default params obtained via
                             MultilevelVolModelParams().
        
        """
        if (levelParams is None):
            levelParams = MultilevelVolModelParams()
        self.priceName = priceName
        self.mean = mean        
        self.levelParams = levelParams
        SimAPI.SimAPI.__init__(self, **kw)

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
        
        PURPOSE:        Create simulation based on parameters given in
                        __init__.
        
        """
        if (preTxList is None):
            preTxList = []
        assert self.endDate.weekday() < 5, 'endDate must be a weekday'
        data, delta = [[self.startDate]], datetime.timedelta(days=1)
        while (data[-1][0] < self.endDate):
            next = data[-1][0] + delta
            while (next.weekday() > 4):
                next += delta
            data.append([next])
            
        query = TimeSeq(['event_date'], data)
        tx = SimTransform(self.levelParams, 'event_date', self.mean)

        query.AddFields(preTxList+[tx])

        retCol = query.GetColIndex(self.levelParams.retNames[-1])
        query.AddBlankColumns([self.priceName])
        query.data[0][-1] = 1
        previous = 1
        for line in query.data[1:]:
            line[-1] = previous * math.exp(line[retCol])
            previous = line[-1]

        return query

class SimTransform(SeqXform):
    """Helper transform used to do simulations.
    
>>> import datetime, random
>>> import MultiClusterSimulator
>>> random.seed(63) # for repeatability
>>> #startDate, endDate = datetime.date(2000,1,3), datetime.date(2009,1,5)
>>> startDate, endDate = datetime.date(1950,1,2), datetime.date(2009,1,5)
>>> query = MultiClusterSimulator.TimeSeq(['event_date'], [[startDate]])
>>> delta = datetime.timedelta(days=1)
>>> while(query.data[-1][0] < endDate):
...     next = query.data[-1][0] + delta
...     while (next.weekday() > 4):
...             next += delta
...     query.data.append([next])
>>> levelNames = ['yearly', 'quarterly', 'monthly', 'weekly', 'daily']
>>> levelFuncs = dict(zip(levelNames, [
... MultiClusterSimulator.GetYear, MultiClusterSimulator.GetQuarter,
... MultiClusterSimulator.GetMonth, MultiClusterSimulator.GetWeek,
... MultiClusterSimulator.GetDay]))
>>> alphas = dict([(n, v) for (n,v) in zip(levelNames,[.05,.1,.1,.1,.1])])
>>> betas = dict([(n, v) for (n,v) in zip(levelNames,[.05,.5,.5,.5,.5])])
>>> omegas = dict([(n, v) for (n,v) in zip(levelNames,[.5,.5,.5,.5,.5])])
>>> omegas[levelNames[0]] = 0.0025
>>> multipliers = dict(zip(levelNames, [1, 4, 12, 52, 262]))
>>> levelParams = MultiClusterSimulator.MultilevelVolModelParams(
... levelNames, levelFuncs, alphas, betas, omegas, multipliers)
>>> tx = MultiClusterSimulator.SimTransform(
... levelParams, 'event_date', 0.0625/260)
>>> query.AddFields([tx])
    """

    def __init__(self, levelParams, dateColName, mean):
        
        levelNames = levelParams.levelNames
        
        self.levelParams = levelParams
        self.dateColName = dateColName
        self.rets = dict([(n, 0.0) for n in levelNames])
        self.vars = dict(self.levelParams.omegas)
        self.dateCol = dateColName
        self.mean = mean
        self.annualizingMults = dict(self.levelParams.multipliers)

        
        for num, name in enumerate(levelNames[1:]):
            self.annualizingMults[name] = (
                self.levelParams.multipliers[name] /
                self.levelParams.multipliers[levelNames[0]])
            self.vars[name] = (
                self.vars[levelNames[num]] * self.levelParams.omegas[name]
                * self.levelParams.multipliers[levelNames[num]]
                / self.levelParams.multipliers[name])

        SeqXform.__init__(self, [dateColName],
                          levelParams.annualizedVolNames + levelParams.retNames)

    def ProcessRowInSeq(self, args, query, line):
        "Override as required by SeqXform to do main computation."
        curDate = args[self.dateColName]

        levelNames = self.levelParams.levelNames
        
        if (line > 0):
            prevDate = query.data[line-1][query.GetColIndex(self.dateColName)]

            for num, name in enumerate(levelNames):
                self._UpdateLevelInfo(num, name, curDate, prevDate, query, line)

        return [math.sqrt(self.vars[n]*self.annualizingMults[n])
                for n in levelNames] + [self.rets[n] for n in levelNames]

    def _UpdateLevelInfo(self, num, name, curDate, prevDate, query, line):
        """Helper method to update info for the current level.
        
        INPUTS:
        
        -- num:        Integer number of the level to update.
        
        -- name:       String name of the level to update. 
        
        -- curDate:    A datetime.date representing current date.    
        
        -- prevDate:   A datetime.date representing previous date.         
        
        -- query:      The raw data so far.  
        
        -- line:       The line in the query we are currently working on. 
        
        -------------------------------------------------------
        
        PURPOSE:        Update self.vars to have the various for the
                        current time and update self.rets to have the
                        appropriate returns for the current time.
        
        
        """
        lFunc = self.levelParams.levelFuncs[name]
        if (lFunc(curDate) != lFunc(prevDate)):
            alphas = self.levelParams.alphas
            betas = self.levelParams.betas
            omegas = self.levelParams.omegas
            multipliers = self.levelParams.multipliers
            if (num == 0):
                prevVarTerm = omegas[name]
                mult = 1
            else:
                prevLevName = self.levelParams.levelNames[num-1]
                prevVarTerm = self.vars[prevLevName] * omegas[prevLevName]
                mult = (multipliers[prevLevName] / float(multipliers[name]))
            self.vars[name] = (prevVarTerm * mult
                               + betas[name] * self.vars[name]
                               + alphas[name] * self.rets[name]**2)
            self.rets[name] = self._ComputeReturnsForLevel(query, line, name)

    def _ComputeReturnsForLevel(self, query, line, name):
        """
        
        INPUTS:

        -- query:      The raw data so far.  
        
        -- line:       The line in the query we are currently working on.

        -- name:       String name of the level to update.         
        
        -------------------------------------------------------
        
        RETURNS:       Return for the given level.
        
        -------------------------------------------------------
        
        PURPOSE:       This method computes the return for the given level
                       name. If it is the lowest level (e.g., daily is
                       often the lowest level), we simulate a new return
                       based on that level's variance. Otherwise, we
                       aggregate the returns from the lowest level for
                       the period.
        
        """
        
        if (name == self.levelParams.levelNames[-1]): #doing lowest level
            result = random.gauss(self.mean, math.sqrt(self.vars[name]))
        else:
            result = 0
            levelFunc = self.levelParams.levelFuncs[name]
            returnCol = query.GetColIndex(self.outputFields[-1])
            dateCol = query.GetColIndex(self.dateColName)
            data = query.data
            line -= 1            
            curLevelValue = levelFunc(data[line][dateCol])
            while (line >= 0 and
                   levelFunc(data[line][dateCol]) == curLevelValue):
                previousReturn = data[line][returnCol]
                if (previousReturn is not None):
                    result += previousReturn
                line -= 1
        return result

def _test():
    "Test docstrings in module."
    import doctest
    doctest.testmod()

if __name__ == "__main__":    
    _test()
    print 'Test finished.'
