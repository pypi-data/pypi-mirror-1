"""
Created on Oct 24, 2009

@author: johnsalvatier

Introduction
------------ 
Implements a variant of DREAM_ZS using PyMC. The sampler is a multi-chain sampler that proposal states based on the differences between 
random past states. The sampler does not use the snooker updater but does use the crossover probability, probability distribution. Convergence
assessment is based on a naive implementation of the Gelman-Rubin convergence statistics; this may be updated to a less naive
 implementation later on.  
 
Academic papers of interest:
 
    Provides the basis for the DREAM_ZS extension (also see second paper).
    C.J.F. ter Braak, and J.A. Vrugt, Differential evolution Markov chain with
    snooker updater and fewer chains, Statistics and Computing, 18(4),
    435-446, doi:10.1007/s11222-008-9104-9, 2008.    
    
    Introduces the origional DREAM idea:
    J.A. Vrugt, C.J.F. ter Braak, C.G.H. Diks, D. Higdon, B.A. Robinson, and
    J.M. Hyman, Accelerating Markov chain Monte Carlo simulation by
    differential evolution with self-adaptive randomized subspace sampling,
    International Journal of Nonlinear Sciences and Numerical
    Simulation, 10(3), 273-290, 2009.
    
    This paper uses DREAM in an application
    J.A. Vrugt, C.J.F. ter Braak, M.P. Clark, J.M. Hyman, and B.A. Robinson,
    Treatment of input uncertainty in hydrologic modeling: Doing hydrology
    backward with Markov chain Monte Carlo simulation, Water Resources
    Research, 44, W00B09, doi:10.1029/2007WR006720, 2008.

Most of the sampler logic takes place in DreamSampler.sample(). DreamSampler contains many MultiChain objects which represent one 
chain, each DreamChain object contains a MultiChainStepper object. The DreamSampler object does the looping and coordinates the step methods
Most of the logic in MultiChain and MultiChainStepper is just pass through logic.
"""
from __future__ import division
from pymc import *

from numpy import *
from  rand_no_replace import *
from gr_convergence import GRConvergence
from multichain import MultiChainSampler, MultiChain
import time 


class DreamSampler(MultiChainSampler):
    """
    DREAM sampling object. 
    
    Contains multiple MultiChain objects which each use a MultiChainStepper step method. 
    The DreamSampler coordinates their stepping.
    """
    
    _numbers = None
    acceptRatio = 0.0
    
    def sample(self, ndraw = 1000, ndraw_max = 20000 , nChains = 5, burnIn = 100, thin = 5, convergenceCriteria = 1.1,  nCR = 3, DEpairs = 1, adaptationRate = .65, eps = 5e-6, mConvergence = False, mAccept = False):
        """
        Samples from a posterior distribution using DREAM.
        
        Parameters
        ----------
        ndraw : int 
            minimum number of draws from the sample distribution to be returned 
        ndraw_max : int 
            maximum number of draws from the sample distribution to be returned
        nChains : int 
            number of different chains to employ
        burnInSize : int
            number of iterations (meaning draws / nChains) to do before doing actual sampling.
        nCR : int
            number of intervals to use to adjust the crossover probability distribution for efficiency
        DEpairs : int 
            number of pairs of chains to base movements off of
        eps : float
            used in jittering the chains
            
        Returns
        -------
            None : None 
                sample sets 
                self.history which contains the combined draws for all the chains
                self.iter which is the total number of iterations 
                self.acceptRatio which is the acceptance ratio
                self.burnIn which is the number of burn in iterations done 
                self.R  which is the gelman rubin convergence diagnostic for each dimension
        """
        
        startTime = time.time()
        
        self.dimension()
        
        dimensions = self._dimensions
        maxChainDraws = floor(ndraw_max/nChains)     
        
        #initialize the history arrays   
        combinedHistory = zeros((nChains * maxChainDraws , dimensions))
        sequenceHistories = zeros((nChains, dimensions, maxChainDraws))
        
        # initialize the temporary storage vectors
        currentVectors = zeros((nChains, dimensions))
        currentLogPs = zeros(nChains)
        
        
        #) make a list of starting chains that at least spans the dimension space
        # in this case it will be of size 2*dim
        nSeedChains = int(ceil(dimensions* 2/nChains) * nChains)
        nSeedIterations = int(nSeedChains/nChains) 

        
        model = self._model_generator()
        for i in range(nSeedIterations - 1): 
            vectors =  zeros((nChains, dimensions))
            for j in range(nChains):
            
                #generate a vector drawn from the prior distributions
                for variable in model:
                    if isinstance(variable,Stochastic) and not variable.observed:
                        drawFromPrior = variable.random()
                        if isinstance(drawFromPrior , np.matrix):
                            drawFromPrior = drawFromPrior.A.ravel()
                        elif isinstance(drawFromPrior, np.ndarray):
                            drawFromPrior = drawFromPrior.ravel()
                        else:
                            drawFromPrior = drawFromPrior
                        
                        vectors[j,self._slices[str(variable)]] = drawFromPrior
            
            #add the vectors to the histories

            sequenceHistories[:,:,i] = vectors
            combinedHistory[i*nChains:(i+1)*nChains,:] = vectors
            
        _chains = []
        #use the last nChains chains as the actual chains to track
        vectors =  zeros((nChains, dimensions))
        for i in range(nChains): 
 
            model = self._model_generator()
            chain = MultiChain(self, model)
            chain.sampleInit(ndraw_max)
        
            vectors[i, :] = chain.currentVector()
            _chains.append(chain)     

        
        #add the starting positions to the history
        sequenceHistories[:,:,nSeedIterations - 1] = vectors
        combinedHistory[(nSeedIterations - 1)*nChains:nSeedIterations*nChains,:] = vectors    
            
        acceptsRatio = 0
        gamma = None       
        self._numbers = arange(nCR)
               
           

                          
        # initilize the convergence diagnostic object
        grConvergence = GRConvergence()
              
        

        
        # get the starting log likelihood and position for each of the chains 
        currentVectors = sequenceHistories[:,:,nSeedIterations - 1]

        for i in range(nChains):
            currentLogPs[i] = copy(_chains[i].logp())
        
        
            
        # initialize the crossover disttribution to be uniform    
        Pm = ones(nCR) / nCR
        L = zeros(nCR)
        deltas= zeros(nCR)
        
        
        #2)now loop through and sample 
        
        minDrawIters = ceil(ndraw / nChains)
        maxIters = ceil(ndraw_max /nChains)
        
        
        iter = 0
    
        
        relevantHistoryStart = 0
        relevantHistoryEnd = nSeedIterations 
       
       
        lastRecalculation = 0
        
        # continue sampling if:
        # 1) we have not drawn enough samples to satisfy the minimum number of iterations
        # 2) or any of the dimensions have not converged 
        # 3) and we have not done more than the maximum number of iterations 

        while ( relevantHistoryStart < burnIn or (relevantHistoryEnd - relevantHistoryStart) *nChains  < ndraw or any(grConvergence.R > convergenceCriteria)) and  relevantHistoryEnd*nChains  < ndraw_max:

            #generate ms from the adapted CR distribution
            m = self._getMs(nChains, Pm)
            
            #generate the associated CRs  
            crProbabilities = (m + 1) / float(nCR)  
            
            #if we are still adapting the CR distribution then record that we have used these Ms  
            if (iter < burnIn):
                L[m] += 1

            # use the CRs to decide whether to update each dimension for each chain
            crDecisions = random.binomial(1, crProbabilities[:, newaxis] , size = (nChains, dimensions) )

            #every5th iteration allow a big jump
            if random.randint(5) == 0.0:
                gamma = array([1.0])
            else:
                gamma = 2.38 / sqrt( 2 * DEpairs  * sum(crDecisions, axis = 1 ))  # sum(crDecision) is the number of dimensioins being updated   
            
            # generate proposal chains 
            proposalVectors = self._propose(currentVectors, combinedHistory, relevantHistoryStart, relevantHistoryEnd, dimensions, nChains, DEpairs, gamma,eps)

            #if iter > (burnIn):
                #print currentVectors - proposalVectors
                
            # if the dimensions is not being updated, then replace the proposalVector with the currentVector
            proposalVectors = choose(crDecisions, (currentVectors, proposalVectors))
            
            # get the log likelihoods for the proposal chains 
            proposalLogPs= zeros(nChains)
            for i in range(nChains):

                _chains[i].propose(proposalVectors[i, :], iter)
                try :
                    proposalLogPs[i] = _chains[i].logp()
                except ZeroProbability:
                    # if the variables are not valid a zero probability excepetion will be raised and we need to deal with that
                    proposalLogPs[i] = -Inf

                    
            #apply the metrop decision to decide whether to accept or reject each chain proposal        
            decisions = self._decide( currentLogPs,proposalLogPs, nChains) 
                
            
            weighting = 1 - exp(-1.0/60) 
            acceptsRatio = weighting * sum(decisions)/nChains + (1-weighting) * acceptsRatio
            if mAccept and iter % 20 == 0:
                print acceptsRatio 
            
            # if we decided to reject the chain, reject it (the default is acceptance)
            for i in range(nChains):
                if decisions[i] == False:
                    _chains[i].reject()
    
            #make the current vectors the previous vectors 
            previousVectors = currentVectors
            currentVectors = choose(decisions[:,newaxis], (currentVectors, proposalVectors))

            currentLogPs = choose(decisions, (currentLogPs, proposalLogPs))
            
            

            #print currentVectors[:,] - previousVectors[:,]
            
            if iter < burnIn:
                # if we are still in the burn in period then update the CR distribution to favor large jumps 
                #calculate the distance
                
                #calculate the stdevs
                vars = var(currentVectors, axis = 0)

                #calculate the standardized jumping distance for each CR used and record it
                deltas[m] = deltas[m] + sum((currentVectors - previousVectors)**2 /vars, axis = 1)
                
                if all(L > 10) and all(deltas > 0) :
                    #modify the distribution of CRs so that it favors updates that lead to large jumps
                    Pm = (iter + 1) * nChains * (deltas / L) / sum(deltas)
                    Pm = Pm / sum(Pm)
                    
            # we only want to recalculate convergence criteria when we are past the burn in period
            # and then only every so often (currently every 10% increase in iterations)
            if (relevantHistoryStart > burnIn  and
                (relevantHistoryEnd - relevantHistoryStart) * nChains > ndraw and  
                iter > lastRecalculation * 1.1):

                lastRecalculation = iter
                # calculate the Gelman Rubin convergence diagnostic 
                grConvergence.update(sequenceHistories, relevantHistoryEnd, relevantHistoryStart, dimensions, nChains)
                if mConvergence:
                    print mean(grConvergence.R), std(grConvergence.R), max(grConvergence.R), argmax(grConvergence.R)

            #record the vector for each chain
            if iter % thin == 0:
                sequenceHistories[:,:,relevantHistoryEnd] = currentVectors
                combinedHistory[(relevantHistoryEnd *nChains) :(relevantHistoryEnd *nChains + nChains),:] = currentVectors
                
                relevantHistoryEnd += 1
                
                # this is where we decide how much of the last samples to use for convergence diagnostics and adaptation
                historyStartMovementRate = adaptationRate
                
                #try to adapt more when the acceptance rate is low and less when it is high 
                if adaptationRate == 'auto':
                    historyStartMovementRate = min((.234/acceptsRatio)*.5, .95)

                relevantHistoryStart += historyStartMovementRate
                
                    
                
            iter += 1

            
            
        
        #3) finalize
        
        # only make the second half of draws available because that's the only part used by the convergence diagnostic
        
        self.history = combinedHistory[relevantHistoryStart*nChains:relevantHistoryEnd*nChains,:]
        self.iter = iter
        self.acceptRatio = acceptsRatio 
        self.burnIn = burnIn 
        self.time = time.time() - startTime
        
        self.R = grConvergence.R
        
        for i in range(nChains):
            _chains[i].sampleFinalize()
            
    def _propose(self, currentVectors, combinedHistory, relevantHistoryStart, relevantHistoryEnd, dimensions, nChains, DEpairs, gamma, eps ):
        """
        generates and returns proposal vectors given the current states
        """
        
        currentIndex = arange((relevantHistoryEnd - 1) *nChains, (relevantHistoryEnd) *nChains)[:, newaxis]

        sampleRange = array(floor(relevantHistoryEnd - relevantHistoryStart), dtype = int) * nChains


        #choose some chains without replacement to combine
        chains = random_no_replace(DEpairs * 2, sampleRange - 1, nChains) + relevantHistoryEnd*nChains - sampleRange
        # makes sure we have already selected the current chain so it is not replaced
        # this ensures that the the two chosen chains cannot be the same as the chain for which the jump is
        chains += (chains >= currentIndex)
        
        chainDifferences =  (sum(combinedHistory[chains[:, 0:DEpairs], :], axis = 1)      - 
                             sum(combinedHistory[chains[:, DEpairs:(DEpairs*2)], :], axis = 1))
        
        e = numpy.random.normal(0, .05,(nChains,dimensions))

        E = numpy.random.normal(0, eps,(nChains,dimensions)) # could replace eps with 1e-6 here

        proposalVectors = currentVectors + (1 + e) * gamma[:,newaxis] * chainDifferences + E
        return proposalVectors
          
    def _getMs(self, nChains, pCRs):
        return sum(self._numbers[newaxis,:] * random.multinomial(1, pCRs, size = nChains), axis = 1)
         
    
    def _decide(self, currentLogPs, proposalLogPs, nChains):
        """
        makes a decision about whether the proposed vector should be accepted
        """
        logMetropRatio = proposalLogPs - currentLogPs
        decision = log(random.uniform(size = nChains)) < logMetropRatio

        return decision 
        
    