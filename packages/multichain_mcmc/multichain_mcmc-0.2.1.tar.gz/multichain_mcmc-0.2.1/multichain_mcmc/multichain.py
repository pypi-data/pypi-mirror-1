'''
Created on Jan 11, 2010

@author: johnsalvatier
'''
from __future__ import division
from pymc import *

from numpy import *
from  rand_no_replace import *
from gr_convergence import GRConvergence
import time 


class MultiChainSampler:
    """
    """
    _model_generator = None
    _chains = []

    
    def __init__(self, model_generator):
        """
        Initializes the sampler.
        
        Parameters
        ----------
            model_generator : func()
                a parameterless function which returns a collection of Stochastics which make up the model. 
                Will be called multiple times, once for each chain. If the Stochastics returned are not identical 
                (for example, based on different data) and distinct (separately instanced) the sampler will have problems.  
        """
        self._model_generator = model_generator 
    
    def dimension(self):
        """Compute the dimension of the sampling space and identify the slices
        belonging to each stochastic.
        """
        self._dimensions = 0
        self._slices = {}
        
        model = self._model_generator()
        for variable in model:
            
            if isinstance(variable,Stochastic) and not variable.observed:

                if isinstance(variable.value, np.matrix):
                    p_len = len(variable.value.A.ravel())
                elif isinstance(variable.value, np.ndarray):
                    p_len = len(variable.value.ravel())
                else:
                    p_len = 1
                    
                self._slices[str(variable)] = slice(self._dimensions, self._dimensions + p_len)
                self._dimensions += p_len
        
        self.slices = self._slices
        
        



class MultiChain(MCMC):
    """
    DreamChain uses a special step method DreamStepper for stepping. It also allows the object controlling it to control
    the looping, proposing and rejecting, which is not possible with other MCMC objects. This allows the chains to be 
    interdependent.
    
    The MCMC._loop() function has been split up into several functions, so that both DREAM and other step methods can be 
    use simultaneously but it is not currently set up to do so, so only DREAM will work right now.
    """
    
    multiChainStepper = None
    
    def __init__(self, container , input=None, variables = None, db='ram', name='MCMC', calc_deviance=True, **kwds):
        """Initialize an MCMC instance.

        :Parameters:
          - input : module, list, tuple, dictionary, set, object or nothing.
              Model definition, in terms of Stochastics, Deterministics, Potentials and Containers.
              If nothing, all nodes are collected from the base namespace.
          - db : string
              The name of the database backend that will store the values
              of the stochastics and deterministics sampled during the MCMC loop.
          - verbose : integer
              Level of output verbosity: 0=none, 1=low, 2=medium, 3=high
          - **kwds :
              Keywords arguments to be passed to the database instantiation method.
        """
        MCMC.__init__(self, input = input, db = db, name = name, calc_deviance = calc_deviance, **kwds)
            
        self.use_step_method(MultiChainStepper, input, container)
        
    
    def sampleInit(self, iter, burn=0, thin=1, tune_interval=1000, tune_throughout=True, save_interval=None, verbose=0):
        """
        sample(iter, burn, thin, tune_interval, tune_throughout, save_interval, verbose)

        Initialize traces, run sampling loop, clean up afterward. Calls _loop.

        :Parameters:
          - iter : int
            Total number of iterations to do
          - burn : int
            Variables will not be tallied until this many iterations are complete, default 0
          - thin : int
            Variables will be tallied at intervals of this many iterations, default 1
          - tune_interval : int
            Step methods will be tuned at intervals of this many iterations, default 1000
          - tune_throughout : boolean
            If true, tuning will continue after the burnin period (True); otherwise tuning
            will halt at the end of the burnin period.
          - save_interval : int or None
            If given, the model state will be saved at intervals of this many iterations
          - verbose : boolean
        """

                
        self.assign_step_methods()

        # find the step method we are now using so we can manipulate it
        for step_method in self.step_methods:
            if type(step_method) == MultiChainStepper:
                self.multiChainStepper = step_method
                


        if burn >= iter:
            raise ValueError, 'Burn interval must be smaller than specified number of iterations.'
        self._iter = int(iter)
        self._burn = int(burn)
        self._thin = int(thin)
        self._tune_interval = int(tune_interval)
        self._tune_throughout = tune_throughout
        self._save_interval = save_interval

        length = int(np.ceil((1.0*iter-burn)/thin))
        self.max_trace_length = length

        # Flags for tuning
        self._tuning = True
        self._tuned_count = 0

        # no longer call the base function because it calls _loop which we are avoiding 
        #Sampler.sample(self, iter, length, verbose)
        #
        
        """
        Draws iter samples from the posterior.
        """
        self._cur_trace_index=0
        self.max_trace_length = iter
        self._iter = iter
        if verbose>0:
            self.verbose = verbose
        self.seed()

        # Initialize database -> initialize traces.
        if length is None:
            length = iter
        self.db._initialize(self._funs_to_tally, length)

        # Put traces on objects
        for v in self._variables_to_tally:
            v.trace = self.db._traces[v.__name__]

        # Loop
        self._current_iter = 0
        
        
        # Set status flag
        self.status='running'

        # Record start time
        start = time.time()
        

    def initStep(self, _current_iter):
        self._current_iter = _current_iter
        
        # primarily taken from MCMC._loop()
        if self.status == 'paused':
            return 

        i = self._current_iter
        
        # Tune at interval
        if i and not (i % self._tune_interval) and self._tuning:
            self.tune()
        
        if i == self._burn:
            if self.verbose>0:
                print 'Burn-in interval complete'
            if not self._tune_throughout:
                if self.verbose > 0:
                    print 'Stopping tuning due to burn-in being complete.'
                self._tuning = False
        
        
        
        
    def continueStep(self):
        
        i = self._current_iter
        # Tell all the step methods except the DREAM StepMethod to take a step (dream step method has already stepped)
        for step_method in self.step_methods:
            
            if step_method != multiChainStepper  : 
                if self.verbose > 2:
                    print 'Step method %s stepping' % step_method._id
                # Step the step method
                step_method.step()
        
        if i % self._thin == 0 and i >= self._burn:
            self.tally()
        
        if self._save_interval is not None:
            if i % self._save_interval==0:
                self.save_state()
        
        if not i % 10000 and i and self.verbose > 0:
            per_step = (time.time() - start)/i
            remaining = self._iter - i
            time_left = remaining * per_step
        
            print "Iteration %i of %i (%i:%02d:%02d remaining)" % (i, self._iter, time_left/3600, (time_left%3600)/60, (time_left%60))
        
        if not i % 1000:
            self.commit()
        
        self._current_iter += 1    
    
    def propose(self, proposalVector, current_iter):
        if self.verbose > 2:
            print 'Step method %s stepping' % step_method._id
        # Step the step method
        self.multiChainStepper.propose(proposalVector)
        
    def currentVector(self):
        return self.multiChainStepper.currentVector()
    
    def logp(self):
        return self.multiChainStepper.logp_plus_loglike
        
    def reject(self):
        self.multiChainStepper.reject()
        
    
    def sampleFinalize(self):
        self._finalize()

class MultiChainStepper(StepMethod):
    
    
    def __init__(self, stochastics, container, verbose = 0, tally = True):
        
        self._container = container
        
        # Initialize superclass
        StepMethod.__init__(self, stochastics, tally=tally)
        
        if verbose is not None:
            self.verbose = verbose
        else:
            self.verbose = stochastic.verbose 
            
    def currentVector(self):
        currentVector = zeros(self._container._dimensions)
        for stochastic in self.stochastics:
            value = 0
            
            if isinstance(stochastic.value, np.matrix):
                value = stochastic.value.A.ravel()
            elif isinstance(stochastic.value, np.ndarray):
                value = stochastic.value.ravel()
            else:
                value = stochastic.value
            
            
            currentVector[self._container._slices[str(stochastic)]] = value
        return currentVector

    def names(self):
        names = [] 
        for stochastic in self.stochastics:
            names.append(str(stochastic))
        return names       
    def propose(self, proposalVector):
        # mostly from adaptive metropolist step method
        
        # Update each stochastic individually.
        for stochastic in self.stochastics:
            proposedValue = proposalVector[self._container._slices[str(stochastic)]]
            if iterable(stochastic.value):
                proposedValue = np.reshape(proposalVector[self._container._slices[str(stochastic)]],np.shape(stochastic.value))
            #if self.isdiscrete[stochastic]:
            #    proposedValue = round_array(proposedValue)
            stochastic.value = proposedValue
            
            
    def reject (self):
        for stochastic in self.stochastics:
            stochastic.revert()
            
            


    