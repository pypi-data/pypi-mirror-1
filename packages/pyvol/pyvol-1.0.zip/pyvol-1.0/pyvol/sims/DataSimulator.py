"""Provides the PriceSimulator class to simulate random asset prices.
"""

import MultiClusterSimulator

# Set the default price simulator to be the MultiClusterSimulator
class PriceSimulator(MultiClusterSimulator.MultiClusterSimulator):
    """Default simulator to use in experiments.

    The PriceSimulator class always just subclasses an existing
    simulator that should be used as the default. This makes it
    easy to have scripts/simulations/experiments always use the
    PriceSimulator.

    The following shows example usage:

>>> import datetime, random, math
>>> import DataSimulator, SimAPI
>>> random.seed(64) # for repeatability
>>> simulator = DataSimulator.PriceSimulator()
>>> query = simulator.MakeSimulatedData()
>>> print SimAPI.MakeStats(query, simulator.levelParams)
yearly    : ret = 0.026, vol = 0.195, sqCorrs = 1.000, 0.123, -0.084
quarterly : ret = 0.025, vol = 0.222, sqCorrs = 1.000, 0.103, 0.138
monthly   : ret = 0.026, vol = 0.223, sqCorrs = 1.000, 0.054, 0.158
weekly    : ret = 0.026, vol = 0.242, sqCorrs = 1.000, 0.175, 0.249
daily     : ret = 0.026, vol = 0.250, sqCorrs = 1.000, 0.422, 0.276
>>> 

    """

def _test():
    "Test docstrings in module."
    import doctest
    doctest.testmod()

if __name__ == "__main__":    
    _test()
    print 'Test finished.'

