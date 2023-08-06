# -*- coding:utf-8 -*-
#-----------------------------------------------------------------------------
# Name:        Melding.py
# Purpose:     The Bayesian melding Class provides
#              uncertainty analyses for simulation models.
#
# Author:      Flávio Codeço Coelho
#
# Created:     2003/08/10
# Copyright:   (c) 2003-2008 by the Author
# Licence:     GPL
#-----------------------------------------------------------------------------
from numpy.core.records import recarray
try:
    import psyco
    psyco.full()
except:
    pass
import sys
import os
import cPickle as CP
import like
import pylab as P
from scipy.stats.kde import gaussian_kde
from scipy.linalg import LinAlgError
from scipy import stats
import numpy
from numpy import array, nan_to_num, zeros, product, exp, ones,mean, var
from time import time
from numpy.random import normal, randint,  random, seed
try:
    from BIP.Viz.realtime import RTplot
    Viz=True
except:
    Viz=False
    print r"""Please install Gnuplot-py to enable realtime visualization.
    http://gnuplot-py.sourceforge.net/
    """
import lhs

from multiprocessing import Pool
if Viz:
    dtplot = RTplot();phiplot = RTplot();thplot = RTplot()

__docformat__ = "restructuredtext en"


class Meld:
    """
    Bayesian Melding class
    """
    def __init__(self,  K,  L, model, ntheta, nphi, alpha = 0.5, verbose = False, viz=False ):
        """
        Initializes the Melding class.
        
        :Parameters:
            - `K`: Number of replicates of the model run. Also determines the prior sample size.
            - `L`: Number of samples from the Posterior distributions. Usually 10% of K.
            - `model`: Callable taking theta as argument and returning phi = M(theta).
            - `ntheta`: Number of inputs to the model (parameters).
            - `nphi`: Number of outputs of the model (State-variables)
            - `verbose`: Boolean: whether to show more information about the computations
            - `viz`: Boolean. Wether to show graphical outputs of the fitting process
        """
        self.K = K
        self.L = L
        self.verbose = verbose
        self.model = model
        self.likelist = [] #list of likelihoods
        self.q1theta = recarray(K,formats=['f8']*ntheta) #Theta Priors (record array)
        self.post_theta = recarray(L,formats=['f8']*ntheta) #Theta Posteriors (record array)
        self.q2phi = recarray(K,formats=['f8']*nphi) #Phi Priors (record array)
        self.phi = recarray(K,formats=['f8']*nphi) #Phi model-induced Priors (record array)
        self.q2type = [] #list of distribution types
        self.post_phi = recarray(L,formats=['f8']*nphi) #Phi Posteriors (record array)
        self.ntheta = ntheta
        self.nphi = nphi
        self.alpha = alpha #pooling weight of user-provided phi priors
        self.done_running = False
        if Viz: #Gnuplot installed
            self.viz = viz
        else:
            self.viz = False
#        self.po = Pool() #pool of processes for parallel processing
    
    def setPhi(self, names, dists=[stats.norm], pars=[(0, 1)], limits=[(-5,5)]):
        """
        Setup the models Outputs, or Phi, and generate the samples from prior distributions 
        needed for the melding replicates.
        
        :Parameters:
            - `names`: list of string with the names of the variables.
            - `dists`: is a list of RNG from scipy.stats
            - `pars`: is a list of tuples of variables for each prior distribution, respectively.
            - `limits`: lower and upper limits on the support of variables.
        """
        if len(names) != self.nphi:
            raise ValueError("Number of names(%s) does not match the number of output variables(%s)."%(len(names),self.nphi))
        self.q2phi.dtype.names = names
        self.phi.dtype.names = names
        self.post_phi.dtype.names = names
        self.plimits = limits
        for n,d,p in zip(names,dists,pars):
            self.q2phi[n] = lhs.lhs(d,p,self.K).ravel()
            self.q2type.append(d.name)


        
    def setTheta(self, names, dists=[stats.norm], pars=[(0, 1)]):
        """
        Setup the models inputs and generate the samples from prior distributions 
        needed for the dists the melding replicates.
        
        :Parameters:
            - `names`: list of string with the names of the parameters.
            - `dists`: is a list of RNG from scipy.stats
            - `pars`: is a list of tuples of parameters for each prior distribution, respectivelydists
        """
        self.q1theta.dtype.names = names
        self.post_theta.dtype.names = names
        if os.path.exists('q1theta'):
            self.q1theta = CP.load(open('q1theta','r'))
        else:
            for n,d,p in zip(names,dists,pars):
                self.q1theta[n] = lhs.lhs(d,p,self.K).ravel()
        
    def setThetaFromData(self,names,data, limits):
        """
        Setup the model inputs and set the prior distributions from the vectors
        in data.
        This method is to be used when the prior distributions are available in 
        the form of a sample from an empirical distribution such as a bayesian
        posterior.
        In order to expand the samples provided, K samples are generated from a
        kernel density estimate of the original sample.
        
        :Parameters:
            - `names`: list of string with the names of the parameters.
            - `data`: list of vectors. Samples of a proposed distribution
            - `limits`: List of (min,max) tuples for each theta to make sure samples are not generated outside these limits.
        """
        self.q1theta.dtype.names = names
        self.post_theta.dtype.names = names
        if os.path.exists('q1theta'):
            self.q1theta = CP.load(open('q1theta','r'))
        else:
            i = 0
            for n,d in zip(names,data):
                smp = []
                while len(smp)<self.K:
                    smp += [x for x in gaussian_kde(d).resample(self.K)[0] if x >= limits[i][0] and x <= limits[i][1]]
                #print self.q1theta[n].shape, array(smp[:self.K]).shape
                self.q1theta[n] = array(smp[:self.K])
                i += 1
#       

    def setPhiFromData(self,names,data,limits):
        """
        Setup the model outputs and set their prior distributions from the
        vectors in data.
        This method is to be used when the prior distributions are available in
        the form of a sample from an empirical distribution such as a bayesian
        posterior.
        In order to expand the samples provided, K samples are generated from a
        kernel density estimate of the original sample.

        :Parameters:
            - `names`: list of string with the names of the variables.
            - `data`: list of vectors. Samples of the proposed distribution.
            - `limits`: list of tuples (ll,ul),lower and upper limits on the support of variables.
        """
        self.q2phi.dtype.names = names
        self.phi.dtype.names = names
        self.post_phi.dtype.names = names
        self.limits = limits
        for n,d in zip(names,data):
            i = 0
            smp = []
            while len(smp)<self.K:
                try:
                    smp += [x for x in gaussian_kde(d).resample(self.K)[0] if x >= limits[i][0] and x <= limits[i][1]]
                except:
                    #d is has no variation, i.e., all elements are the same
                    #print d
                    #raise LinAlgError, "Singular matrix"
                    smp = ones(self.K)*d[0] #in this case return a constant sample
            self.q2phi[n] = array(smp[:self.K])
            self.q2type.append('empirical')
            i += 1
        #self.q2phi = self.filtM(self.q2phi, self.q2phi, limits)

        
    def run(self,*args):
        """
        Runs the model through the Melding inference.model
        model is a callable which return the output of the deterministic model,
        i.e. the model itself.
        The model is run self.K times to obtain phi = M(theta).
        """
        
        for i in xrange(self.K):
            theta = [self.q1theta[n][i] for n in self.q1theta.dtype.names]
            r = self.po.apply_async(self.model, theta)
            self.phi[i]= r.get()[-1]#self.model(*theta)[-1] #phi is the last point in the simulation

        self.done_running = True
        
    def getPosteriors(self,t):
        """
        Updates the posteriors of the model's output for the last t time steps.
        Returns two record arrays:
        - The posteriors of the Theta
        - the posterior of Phi last t values of time-series. self.L by `t` arrays.

        :Parameters:
            - `t`: length of the posterior time-series to return.
        """
        if not self.done_running:
            return
        if t > 1:
            self.post_phi = recarray((self.L,t),formats=['f8']*self.nphi)
            self.post_phi.dtype.names = self.phi.dtype.names
        def cb(r):
            '''
            callback function for the asynchronous model runs.
            r: tuple with results of simulation (results, run#)
            '''
            if t == 1:
                self.post_phi[r[1]] = (r[0][-1],)
                #self.post_phi[r[1]]= [tuple(l) for l in r[0][-t:]]
            else:
                self.post_phi[r[1]]= [tuple(l) for l in r[0][-t:]]
        po = Pool()
        #random indices for the marginal posteriors of theta
        pti = lhs.lhs(stats.randint,(0,self.L),siz=(self.ntheta,self.L))
        for i in xrange(self.L):#Monte Carlo with values of the posterior of Theta
            theta = [self.post_theta[n][pti[j,i]] for j,n in enumerate(self.post_theta.dtype.names)]
            po.apply_async(enumRun, (self.model,theta,i), callback=cb)
#            r = po.apply_async(self.model,theta)
#            if t == 1:
#                self.post_phi[i] = r.get()[-1]
#            else:
#                self.post_phi[i]= [tuple(l) for l in r.get()[-t:]]
            if i%100 == 0 and self.verbose:
                print "==> L = %s"%i

        po.close()
        po.join()
        return self.post_theta, self.post_phi

    def filtM(self,cond,x,limits):
        '''
        Multiple condition filtering.
        Remove values in x[i], if corresponding values in
        cond[i] are less than limits[i][0] or greater than
        limits[i][1].

        :Parameters:
            - `cond`: is an array of conditions.
            - `limits`: is a list of tuples (ll,ul) with length equal to number of lines in `cond` and `x`.
            - `x`: array to be filtered.
        '''
        # Deconstruct the record array, if necessary.
        names = []
        if isinstance(cond, recarray):
            names = list(cond.dtype.names)
            cond = [cond[v] for v in cond.dtype.names]
            x = [x[v] for v in x.dtype.names]

        cond = array(cond)
        cnd = ones(cond.shape[1],int)
        for i,j in zip(cond,limits):
            ll = j[0]
            ul = j[1]
            #print cond.shape,cnd.shape,i.shape,ll,ul
            cnd = cnd & less(i,ul) & greater(i,ll)
        f = compress(cnd,x, axis=1)

        if names:#Reconstruct the record array
            r = recarray((1,f.shape[1]),formats=['f8']*len(names),names=names)
            for i,n in enumerate(names):
                r[n]=f[i]
            f=r

        return f

    def basicfit(self,s1,s2):
        '''
        Calculates a basic fitness calculation between a model-
        generated time series and a observed time series.
        it uses a normalized RMS variation.

        :Parameters:
            - `s1`: model-generated time series. record array.
            - `s2`: observed time series. dictionary with keys matching names of s1

        :Return:
            Root mean square deviation between ´s1´ and ´s2´.
        '''
        fit = []
        for k in s2.keys():
            if s2[k] == [] or (not s2[k].any()):
                continue #no observations for this variable
            e = numpy.sqrt(mean((s1[k]-s2[k])**2.))
            fit.append(e) #min to guarantee error is bounded to (0,1)

        return mean(fit) #mean r-squared
        

    def logPooling(self,phi):
        """
        Returns the probability associated with each phi[i]
        on the pooled pdf of phi and q2phi.

        :Parameters:
            - `phi`: prior of Phi induced by the model and q1theta.
        """
        
#       Estimating the multivariate joint probability densities
        phidens = gaussian_kde(array([phi[n][:,-1] for n in phi.dtype.names]))

        q2dens = gaussian_kde(array([self.q2phi[n] for n in self.q2phi.dtype.names]))
#       Determining the pooled probabilities for each phi[i]
#        qtilphi = zeros(self.K)
        lastp = array([list(phi[i,-1]) for i in xrange(self.K)])
#        print lastp,lastp.shape
        qtilphi = (phidens.evaluate(lastp.T)**(1-self.alpha))*q2dens.evaluate(lastp.T)**self.alpha
        return qtilphi/sum(qtilphi)

    def abcRun(self,fitfun=None, data={}, t=1,nopool=False,savetemp=False):
        """
        Runs the model for inference through Approximate Bayes Computation
        techniques. This method should be used as an alternative to the sir.
        
        :Parameters:
             - `fitfun`: Callable which will return the goodness of fit of the model to data as a number between 0-1, with 1 meaning perfect fit
             - `t`: number of time steps to retain at the end of the of the model run for fitting purposes.
             - `data`: dict containing observed time series (lists of length t) of the state variables. This dict must have as many items the number of state variables, with labels matching variables names. Unorbserved variables must have an empty list as value.
             - `savetemp`: Should temp results be saved. Useful for long runs. Alows for resuming the simulation from last sa
        """
        seed()
        if not fitfun:
            fitfun = self.basicfit
        if savetemp:
            CP.dump(self.q1theta,open('q1theta','w'))
#       Running the model ==========================
        phi = self.runModel(savetemp,t)

        print "==> Done Running the K replicates\n"
        # Do Log Pooling
        if nopool:
            qtilphi = ones(self.K)
        else:
            t0 = time()
            qtilphi = self.logPooling(phi) #vector with probability of each phi[i] belonging to qtilphi
            print "==> Done Running the Log Pooling (took %s seconds)\n"%(time()-t0)
            qtilphi = nan_to_num(qtilphi)
            #print 'max(qtilphi): ', max(qtilphi)
            if sum(qtilphi)==0:
                print 'Pooled prior on ouputs is null, please check your priors, and try again.'
                return 0
#      
#        calculate weights
        w = [fitfun(phi[i],data) for i in xrange(phi.shape[0])]
        w /=sum(w)
        w = 1-w
        #print "w=",w, mean(w), var(w)
#        print
#        print 'qtilphi=',qtilphi
        # Resampling Thetas
        w = nan_to_num(w)
        w = array(w)*qtilphi
        w /=sum(w)
        w = nan_to_num(w)
        print 'max(w): %s\nmean(w): %s\nvar(w): %s'%(max(w), mean(w), var(w))
#        for n in phi.dtype.names:
#            P.plot(mean(phi[n],axis=0),label=n)
#        P.figure()
#        P.plot(w,label='w')
#        P.plot(qtilphi,label='qtilphi')
#        P.title('Resampling vector(w) and pooled prior on Phi')
#        P.legend()
        if sum(w) == 0.0:
            print 'Resampling weights are all zero, please check your model or data.'
            return 0
        t0 = time()
        j = 0
        while j < self.L: # Extract L samples from q1theta
            i=randint(0,w.size)# Random position of w and q1theta
            if random()<= w[i]:
                self.post_theta[j] = self.q1theta[i]# retain the sample according with resampling prob.
                j+=1
        print "==> Done Resampling (L=%s) priors (took %s seconds)"%(self.L,(time()-t0))

        self.done_running = True
        return 1

    def sir(self, data={}, t=1,variance=0.1, nopool=False,savetemp=False):
        """
        Run the model output through the Sampling-Importance-Resampling algorithm.
        Returns 1 if successful or 0 if not.

        :Parameters:
            - `data`: observed time series on the model's output
            - `t`: length of the observed time series
            - `variance`: variance of the Normal likelihood function
            - `nopool`: True if no priors on the outputs are available. Leads to faster calculations
            - `savetemp`: Boolean. create a temp file?
        """
        seed()
        phi = self.runModel(savetemp,t)
        # Do Log Pooling
        if nopool:
            qtilphi = ones(self.K)
        else:
            t0 = time()
            qtilphi = self.logPooling(phi) #vector with probability of each phi[i] belonging to qtilphi
            print "==> Done Running the Log Pooling (took %s seconds)\n"%(time()-t0)
            qtilphi = nan_to_num(qtilphi)
            print 'max(qtilphi): ', max(qtilphi)
            if sum(qtilphi)==0:
                print 'Pooled prior on ouputs is null, please check your priors, and try again.'
                return 0

#        Calculating the likelihood of each phi[i] considering the observed data
        lik = zeros(self.K)
        t0=time()
#        po = Pool()
        for i in xrange(self.K):
            l=1
            for n in data.keys():
                if isinstance(data[n],list) and data[n] == []: 
                    continue #no observations for this variable
                elif isinstance(data[n],numpy.ndarray) and (not data[n].any()):
                    continue #no observations for this variable
                p = phi[n]
                
#                liklist=[po.apply_async(like.Normal,(data[n][m], j, tau)) for m,j in enumerate(p[i])]
#                l=product([p.get() for p in liklist])
                l *= product([exp(like.Normal(data[n][m], j,1./(variance))) for m,j in enumerate(p[i])])
                #l += sum([like.Normal(data[n][m], j,1./(tau*j+.0001)) for m,j in enumerate(p[i])])
            
            lik[i]=l
#        po.close()
#        po.join()
        if self.viz:
            dtplot.clearFig();phiplot.clearFig();thplot.clearFig()
            dtplot.gp.xlabel('observed')
            dtplot.gp.ylabel('simulated')
            obs = [];sim =[]
            for n in data.keys():
                obs.append(data[n])
                sim.append(phi[n].mean(axis=0).tolist())
            dtplot.scatter(array(obs),array(sim),names=data.keys(),title='fit')
            phiplot.plotlines(array(sim),names=data.keys(),title='Model Output')
            thplot.plothist(self.q1theta, title='Input parameters',names=self.q1theta.dtype.names)
        print "==> Done Calculating Likelihoods (took %s seconds)"%(time()-t0)
        lr = nan_to_num(max(lik)/min(lik))
        print '==> Likelihood (min,mean,max,sum): ',min(lik),mean(lik),max(lik), sum(lik)
        print "==> Likelihood ratio of best run/worst run: %s"%(lr,)
#        Calculating the weights
        w = nan_to_num(qtilphi*lik)
        w = nan_to_num(w/sum(w))

        if not sum(w) == 0.0:
            j = 0
            t0 = time()
            maxw = 0;minw = max(w) #keep track of goodness of fit of phi
            while j < self.L: # Extract L samples from q1theta
                i=randint(0,w.size)# Random position of w and q1theta
                if random()*max(w)<= w[i]:
                    self.post_theta[j] = self.q1theta[i]# retain the sample according with resampling prob.
                    maxw = max(maxw,w[i])
                    minw = min(minw,w[i])
                    j+=1
                    if not j%100 and self.verbose:
                        print j, "of %s"%self.L
            self.done_running = True
            print "==> Done Resampling (L=%s) priors (took %s seconds)"%(self.L,(time()-t0))
            wr = maxw/minw
            print "==> Likelihood ratio of best/worst retained runs: %s"%(wr,)
            if wr == 1:
                print "==> Flat likelihood, trying again..."
                return 0
            print "==> Improvement: %s percent"%(100-100*wr/lr,)
        else:
            print 'Resampling weights are all zero, please check your model or data, and try again.\n'
            print '==> Likelihood (min,mean,max): ',min(lik),mean(lik),max(lik)
            print '==> RMS deviation of outputs: %s'%(self.basicfit(phi, data),)
            return 0
        return 1

    def runModel(self,savetemp,t=1):
        '''
        Handles running the model self.K times keeping a temporary savefile for 
        resuming calculation in case of interruption.

        :Parameters:
            - `savetemp`: Boolean. create a temp file?
        '''
        if savetemp:
            CP.dump(self.q1theta,open('q1theta','w'))
#       Running the model ==========================
        
                
        if os.path.exists('phi.temp'):
            self.phi,j = CP.load(open('phi.temp','r'))
        else:
            j=0
            self.phi = recarray((self.K,t),formats=['f8']*self.nphi, names = self.phi.dtype.names)
        def cb(r):
            '''
            callback function for the asynchronous model runs
            '''
            if t == 1:
                self.phi[r[1]] = (r[0][-1],)
            else:
                self.phi[r[1]] = [tuple(l) for l in r[0][-t:]]# #phi is the last t points in the simulation

        po = Pool()
        t0=time()
        for i in xrange(j,self.K):
            theta = [self.q1theta[n][i] for n in self.q1theta.dtype.names]
            r = po.apply_async(enumRun,(self.model,theta,i),callback=cb)
#            r = po.apply_async(self.model,theta)
#            if t == 1:
#                phi[i] = (r.get()[-1],)
#            else:
#                phi[i] = [tuple(l) for l in r.get()[-t:]]# #phi is the last t points in the simulation
            if i%100 == 0 and self.verbose:
                print "==> K = %s"%i
                if savetemp:
                    CP.dump((self.phi,i),open('phi.temp','w'))
        if savetemp: #If all replicates are done, clear temporary save files.
            os.unlink('phi.temp')
            os.unlink('q1theta')
        po.close()
        po.join()
        print "==> Done Running the K (%s) replicates (took %s seconds)\n"%(self.K,(time()-t0))
        
        return self.phi
def enumRun(model,theta,k):
    """
    Returns model results plus run number.

    :Parameters:
        - `model`: model callable
        - `theta`: model input list
        - `k`: run number
        
    :Return:
        - res: result list
        - `k`: run number
    """
    res =model(*theta)
    return (res,k)

def model(r, p0, n=1):
    """
    Model (r,p0, n=1)
    Simulates the Population dynamic Model (PDM) Pt = rP0
    for n time steps.
    P0 is the initial population size. 
    Example model for testing purposes.
    """
#    print "oi"
    Pt = zeros(n, float) # initialize the output vector
    P = p0
    for i in xrange(n):
        Pt[i] = r*P
        P = Pt[i]
    
    return Pt


def plotRaHist(arr):
    '''
    Plots a record array
    as a panel of histograms
    '''
    nv = len(arr.dtype.names)
    fs = (numpy.ceil(numpy.sqrt(nv)),numpy.floor(numpy.sqrt(nv))+1) #figure size
    P.figure()
    for i,n in enumerate(arr.dtype.names):
        P.subplot(nv/2+1,2,i+1)
        P.hist(arr[n],bins=50, normed=1, label=n)
        P.legend()


def main2():
    start = time()
    Me = Meld(K=5000,L=1000,model=model, ntheta=2,nphi=1,verbose=False,viz=False)
    Me.setTheta(['r','p0'],[stats.uniform,stats.uniform],[(2,4),(0,5)])
    Me.setPhi(['p'],[stats.uniform],[(6,9)],[(6,9)])
    #Me.add_data(normal(7.5,1,400),'normal',(6,9))
    #Me.run()
    Me.sir(data ={'p':[7.5]} )
    pt,pp = Me.getPosteriors(1)
    end = time()
    plotRaHist(pt)
    plotRaHist(pp)
    P.show()
    print end-start, ' seconds'

if __name__ == '__main__':
    
    main2()
     

