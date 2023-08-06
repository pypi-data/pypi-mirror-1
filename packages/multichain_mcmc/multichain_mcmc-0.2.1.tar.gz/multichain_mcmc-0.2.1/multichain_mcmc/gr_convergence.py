from __future__ import division
import numpy
'''
Created on Jan 11, 2010

@author: johnsalvatier
'''

class GRConvergence:
    """
    Gelman Rubin convergence diagnostic calculator class. It currently only calculates the naive
    version found in the first paper. It does not check to see whether the variances have been
    stabilizing so it may be misleading sometimes.
    """
    _R = numpy.Inf
    
    def __init__(self):
        pass
    
    def _get_R(self):
        return self._R
    
    R = property(_get_R)
    
    
    def update(self, sequences, relevantHistoryEnd, relevantHistoryStart, dimensions, nChains):
        """
        Updates the convergence diagnostic with the current history.
        """
        
        start = relevantHistoryStart 
        end = relevantHistoryEnd
        N = end - start
        
        sequences = sequences[:,:,start:end]

        variances  = numpy.var(sequences,axis = 2)

        means = numpy.mean(sequences, axis = 2)
        
        withinChainVariances = numpy.mean(variances, axis = 0)
        
        betweenChainVariances = numpy.var(means, axis = 0) * N
        
        varEstimate = (1 - 1.0/N) * withinChainVariances + (1.0/N) * betweenChainVariances

        self._R = numpy.sqrt(varEstimate/ withinChainVariances)