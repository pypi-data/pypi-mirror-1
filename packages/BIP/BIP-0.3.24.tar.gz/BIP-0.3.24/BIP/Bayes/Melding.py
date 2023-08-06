# -*- coding:utf-8 -*-
#-----------------------------------------------------------------------------
# Name:        Melding.py
# Purpose:     The Bayesian melding Class provides
#              uncertainty analyses for simulation models.
#
# Author:      Flávio Codeço Coelho
#
# Created:     2003/08/10
# Copyright:   (c) 2003-2009 by the Author
# Licence:     GPL v3
#-----------------------------------------------------------------------------
from numpy.core.records import recarray
try:
    import psyco
    psyco.full()
except:
    pass
import sys
import os
import copy
import cPickle as CP
import like
import pylab as P
from scipy.stats.kde import gaussian_kde
from scipy.linalg import LinAlgError
from scipy import stats,  optimize as optim
import numpy
from numpy import array, nan_to_num, zeros, product, exp, ones,mean, var,sqrt,floor
from time import time
from numpy.random import normal, randint,  random, seed
import PlotMeld as PM
from BIP.Bayes.Samplers import MCMC
try:
    from BIP.Viz.realtime import RTplot
    Viz=True
except:
    Viz=False
    print r"""Please install Gnuplot-py to enable realtime visualization.
    http://gnuplot-py.sourceforge.net/
    """
import lhs

from multiprocessing import Pool, Process
if Viz:
    dtplot = RTplot();phiplot = RTplot();thplot = RTplot()

__docformat__ = "restructuredtext en"

class FitModel(object):
    """
    Fit a model to data generating
    Bayesian posterior distributions of input and
    outputs of the model.
    """
    def __init__(self, K,L,model, ntheta, nphi,inits,tf,thetanames,phinames,wl=None ,nw=1,verbose=False,  burnin=1000):
        """
        Initialize the model fitter.

        :Parameters:
            - `K`: Number of samples from the priors. On MCMC also the number of samples of the posterior.
            - `L`: Number of samples of the posteriors. Only used on SIR and ABC methods.
            - `model`: Callable (function) returning the output of the model, from a set of parameter values received as argument.
            - `ntheta`: Number of parameters included in the inference.
            - `nphi`: Number of outputs of the model.
            - `inits`: inits initial values for the model's variables.
            - `tf`: Length of the simulation, in units of time.
            - `phinames`: List of names (strings) with names of the model's variables
            - `thetanames`: List of names (strings) with names of parameters included on the inference.
            - `wl`: window lenght length of the inference window.
            - `nw`: Number of windows to analyze on iterative inference mode
            - `verbose`: Verbose output if True.
            - `burnin`: number of burnin samples, used in the case on mcmc method.
        """
        try:
            assert wl<=tf
        except AssertionError:
           sys.exit("Window Length cannot be larger that Length of the simulation(tf)" )
        self.K = K
        self.L = L
        self.finits = inits
        self.ftf = tf
        self.inits = inits
        self.tf = tf
        self.totpop = sum(inits)
        self.model = model
        self.model.func_globals['inits'] = self.inits
        self.model.func_globals['tf'] = self.tf
        self.nphi = nphi
        self.ntheta = ntheta
        self.phinames = phinames
        self.thetanames = thetanames
        self.wl = wl
        self.nw = nw
        self.done_running = False
        self.prior_set = False
        self.burnin = burnin
        self.pool = False #this will be updated by the run method.
        self.Me = Meld(K=K,L=L,model=self.model,ntheta=ntheta,nphi=nphi,verbose=verbose)
#    @property
#    def inits(self):
#        return self._inits
#    @inits.setter
#    def inits(self, value):
#        self.model.func_globals['inits']=value
#        self._inits = value
#    @property
#    def tf(self):
#        return self._tf
#    @tf.setter
#    def tf(self, value):
#        self.model.func_globals['tf']=value
#        self._tf = value

    def optimize(self, data, p0):
        """
        Finds best parameters using an optimization approach
        """
        def mse(theta):
            s1 = self.Me.model_as_ra(theta)
            return self._rms_error(s1, data)
        potimo = optim.anneal(mse, p0)[0]
        return potimo
        
    def _rms_error(self, s1, s2):
        '''
        Calculates a the error between a model-
        generated time series and a observed time series.
        It uses a normalized RMS deviation.

        :Parameters:
            - `s1`: model-generated time series. 
            - `s2`: observed time series. dictionary with keys matching names of s1
        :Types:
            - `s1`: Record array or list.
            - `s2`: Dictionary or list
        
        s1 and s2 can also be both lists of lists or lists of arrays of the same length.

        :Return:
            The Root mean square deviation between `s1` and `s2`.
        '''
        if isinstance(s1, recarray):
            assert isinstance(s2, dict)
            err = []
            for k in s2.keys():
                e = mean((s1[k]-s2[k])**2./s2[k]**2)
                err.append(e) 
        elif isinstance(s1, list):
            assert isinstance(s2, list) and len(s1) ==len(s2)
            err = [mean((s-t)**2./t**2) for s, t in zip(s1, s2)]
        rmsd = nan_to_num(mean(err))
        return rmsd
        
    def set_priors(self,tdists,tpars, tlims,pdists,ppars,plims):
        """
        Set the prior distributions for Phi and Theta

        :Parameters:
            - `pdists`: distributions for the output variables. For example: [scipy.stats.uniform,scipy.stats.norm]
            - `ppars`: paramenters for the distributions in pdists. For example: [(0,1),(0,1)]
            - `plims`: Limits of the range of each phi. List of (min,max) tuples.
            - `tdists`: same as pdists, but for input parameters (Theta).
            - `tpars`: same as ppars, but for tdists.
            - `tlims`: Limits of the range of each theta. List of (min,max) tuples.
        """
        self.pdists = pdists
        self.ppars = ppars
        self.plims = plims
        self.tdists = tdists
        self.tpars = tpars
        self.tlims = tlims
        self._init_priors()
        self.prior_set = True
    
    def prior_sample(self):
        """
        Generates a set of sample from the starting theta prior distributions
        for reporting purposes.
        
        :Returns:
            Dictionary with (name,sample) pairs
        """
        s = {}
        for i, n in enumerate(self.thetanames):
            s[n]=self.tdists[i](*self.tpars[i]).rvs(self.K)
        return s
            
    def _init_priors(self, prior=None):
        """
        """
        if prior!=None and prior['theta'] and prior['phi']:
            self.Me.setThetaFromData(self.thetanames,prior['theta'],self.tlims)
            self.Me.setPhiFromData(self.phinames,prior['phi'],self.plims)
        else:
            print "++++>"
            self.Me.setTheta(self.thetanames,self.tdists,self.tpars, self.tlims)
            self.Me.setPhi(self.phinames,self.pdists,self.ppars,self.plims)
            
    def do_inference(self, prior, data, predlen, method, likvar):
        """
        """
        self._init_priors(prior)
        succ=0
        att = 1
        for n in data.keys():
            if n not in self.phinames:
                data.pop(n)
        if method == "SIR":
            while not succ: #run sir Until is able to get a fit
                print 'attempt #',att
                succ = self.Me.sir(data=data,variance=likvar,pool=self.pool,t=self.tf)
                att += 1
        elif method == "MCMC":
            while not succ: #run sir Until is able to get a fitd == "mcmc":
                print 'attempt #',att
                succ = self.Me.mcmc_run(data,t=self.tf,likvariance=likvar,burnin=self.burnin)

        elif method == "ABC":
            #TODO: allow passing of fitfun
            self.Me.abcRun(data=data,fitfun=None,pool=self.pool, t=self.tf)
        pt,series = self.Me.getPosteriors(t=self.tf)
        pp = series[:,-1]
#        print "var:", numpy.std(series.I[:, 0])
#        for i, s in enumerate(series):
#                try:
#                    assert tuple(s[0]) == tuple(self.inits) 
#                except AssertionError:
#                    print i, ":", s[0]
#                    print self.inits
        # TODO: figure out what to do by default with inits
        if self.nw >1:
            adiff = array([abs(pp[vn]-data[vn][-1]) for vn in data.keys()])
            diff = adiff.sum(axis=0) #sum errors for all oserved variables
            initind = diff.tolist().index(min(diff))
            self.inits = [pp[vn][initind] for vn in self.phinames]
            for i, v in enumerate(self.phinames):
                if v in data.keys():
                    self.inits[i] = data[v][-1] 
            self.model.func_globals['inits'] = self.inits
        
        if predlen:
            predseries = self.Me.getPosteriors(predlen)[1]
        return pt,pp,series,predseries,att

    def run(self, data,method,likvar,pool=False,adjinits=True,  monitor=False):
        """
        Fit the model against data

        :Parameters:
            - `data`: dictionary with variable names and observed series, as Key and value respectively.
            - `method`: Inference method: "ABC", "SIR" or "MCMC"
            - `likvar`: Variance of the likelihood function in the SIR and MCMC method
            - `pool`: Pool priors on model's outputs.
            - `adjinits`: whether to adjust inits to data
            - `monitor`: Whether to monitor certains variables during the inference. If not False, should be a list of valid phi variable names.
        """
        self.pool = pool
        if not self.prior_set: return
        if monitor:
            self._monitor_setup()
        start = time()
        d = data
        prior = {'theta':[],'phi':[]}
        os.system('rm wres_*')
        if self.wl == None:
            self.wl = floor(len(d.values()[0])/self.nw)
        wl = self.wl
        for w in range(self.nw):
            print '==> Window # %s of %s!'%(w+1,self.nw)
            self.tf=wl
            self.model.func_globals['tf'] = wl
            d2 = {}
            for k,v in d.items():#Slicing data to the current window
                d2[k] = v[w*wl:w*wl+wl]            
            if w==0 and adjinits:
                for n in d2.keys():
                    if n not in self.phinames:
                        continue
                    i = self.phinames.index(n)
                    self.inits[i] = d2[n][0]
                    #TODO: figure out how to balance the total pop
#                    self.inits[0] += self.totpop-sum(self.inits) #adjusting sunceptibles
                    self.model.func_globals['inits'] = self.inits
            pt,pp,series,predseries,att = self.do_inference(data=d2, prior=prior,predlen=wl, method=method,likvar=likvar)
            #print series[:, 0], self.inits
            f = open('wres_%s'%w,'w')
            #save weekly posteriors of theta and phi, posteriors of series, data (d) and predictions(z)
            CP.dump((pt,pp,series,d,predseries, att*self.K),f)
            f.close()
            prior = {'theta':[],'phi':[]}
            for n in pt.dtype.names:
                prior['theta'].append(pt[n])
            #beta,alpha,sigma,Ri  = median(pt.beta),median(pt.alpha),median(pt.sigma),median(pt.Ri
            for n in pp.dtype.names:
                #print compress(isinf(pp[n]),pp[n])
                prior['phi'].append(pp[n])
            if monitor:
                self._monitor_plot(series,prior,d2,w,data,vars=monitor)
        print "time: %s seconds"%(time()-start)
        self.done_running = True


    def _monitor_setup(self):
        """
        Sets up realtime plotting of inference
        """
        self.hst = RTplot() #theta histograms
        self.fsp = RTplot()#full data and simulated series
        self.ser = RTplot()# phi time series

    def _get95_bands(self,series,vname):
        i5 = array([stats.scoreatpercentile(t,2.5) for t in series[vname].T])
        i95 = array([stats.scoreatpercentile(t,97.5) for t in series[vname].T])
        return i5,i95
    def _monitor_plot(self, series, prior, d2,w,data, vars):
        """
        Plots real time data
        """
        
        diff = array([abs(series[vn][:, -1]-d2[vn][-1]) for vn in d2.keys()]).sum(axis=0) #sum errors for all oserved variables
        initind = diff.tolist().index(min(diff))
        for n in vars:
            if n not in d2:
                continue
            i5,i95 = self._get95_bands(series,n)
            self.ser.plotlines(data=series[n][initind],  names=["Best run's %s"%n], title='Window %s'%(w+1))
            self.ser.plotlines(data=i5, names=['2.5%'])
            self.ser.plotlines(data=i95, names=['97.5%'])
            self.ser.plotlines(d2[n],style='points', names=['Obs. %s'%n])
            self.fsp.plotlines(data[n],style='points', names=['Obs. %s'%n], title='Window %s'%(w+1))
        self.hst.plothist(data=array(prior['theta']),names=list(self.thetanames),title='Window %s'%(w+1))
        cpars = [prior['theta'][i][initind] for i in range(self.ntheta)]
        self.model.func_globals['inits'] = self.finits; self.model.func_globals['tf'] = self.ftf
        simseries = self.model(*cpars)
        self.model.func_globals['inits'] = self.inits; self.model.func_globals['tf'] = self.tf
        self.fsp.plotlines(data=simseries.T, names=list(self.phinames), title="Best fit simulation after window %s"%(w+1))
        self.ser.clearFig()
        self.hst.clearFig()
        self.fsp.clearFig()
    
    def plot_results(self, names=[]):
        """
        Plot the final results of the inference
        """
        if not names:
            names = self.phinames
        try: #read the data files
            pt,pp,series,predseries,obs = self._read_results()
        except:
            if not self.done_running:
                return
        if obs.has_key('time'):
            tim = numpy.array(obs['time'])
        else:
            tim = numpy.arange(self.nw*self.wl)
        #PM.plot_par_series(range(len(pt)),pt)
        priors = self.prior_sample()
        PM.plot_par_violin(range(len(pt)),pt, priors)
        PM.plot_series2(tim,obs,series,names=names, wl=self.wl)
        if self.nw > 1:
            PM.pred_new_cases(obs,predseries,self.nw,names,self.wl)
            PM.plot_series2(tim,obs,predseries,names=names,
                            title='Predicted vs. Observed series',lag=True)
        P.show()

    def _read_results(self):
        """
        read results from disk
        """
        pt,pp,series,predseries = [],[],[],[]
        for w in range(self.nw):
            fn = 'wres_%s'%w
            print fn
            f = open(fn,'r')
            a,b,c,obs,pred, samples = CP.load(f)
            f.close()
            pt.append(a)
            pp.append(b)
            series.append(c)
            predseries.append(pred)
        return pt,pp,series,predseries,obs
            

class Meld(object):
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
        self.thetapars = []
        self.phipars = []
        self.alpha = alpha #pooling weight of user-provided phi priors
        self.done_running = False
        self.theta_dists = {}#parameterized rngs for each parameter
        self.phi_dists = {}#parameterized rngs for each variable
        self.proposal_variance = 0.0000001
        self.adaptscalefactor = 1 #adaptive variance. Used my metropolis hastings
        self.salt_band = 0.1
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
        self.phipars = pars
        for n,d,p in zip(names,dists,pars):
            self.q2phi[n] = lhs.lhs(d,p,self.K).ravel()
            self.q2type.append(d.name)
            self.phi_dists[n]=d(*p)


        
    def setTheta(self, names, dists=[stats.norm], pars=[(0, 1)], lims=[(0, 1)]):
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
        self.thetapars = pars
        self.tlimits = lims
        if os.path.exists('q1theta'):
            self.q1theta = CP.load(open('q1theta','r'))
        else:
            for n,d,p in zip(names,dists,pars):
                self.q1theta[n] = lhs.lhs(d,p,self.K).ravel()
                self.theta_dists[n]=d(*p).rvs
        
    def add_salt(self,dataset,band):
        """
        Adds a few extra uniformly distributed data 
        points beyond the dataset range.
        This is done by adding from a uniform dist.
        
        :Parameters:
            - `dataset`: vector of data
            - `band`: Fraction of range to extend [0,1[
            
        :Returns:
            Salted dataset.
        """
        dmax = max(dataset)
        dmin = min(dataset)
        drange = dmax-dmin
        hb = drange*band/2.
        d = numpy.concatenate((dataset,stats.uniform(dmin-hb,dmax-dmin+hb).rvs(self.K*.05)))
        return d
    
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
        self.tlimits = limits
        tlimits = dict(zip(names,limits))
        class Proposal:
            def __init__(self,name, dist):
                self.name = name
                self.dist = dist
            def __call__(self):
                smp = -numpy.inf
                while not (smp>=tlimits[self.name][0] and smp<=tlimits[self.name][1]):
                    smp = self.dist.resample(1)[0][0]
                return smp
                
        if os.path.exists('q1theta'):
            self.q1theta = CP.load(open('q1theta','r'))
        else:
            for n,d,lim in zip(names,data,limits):
                smp = []
                #add some points uniformly across the support 
                #to help MCMC to escape from prior bounds
                salted = self.add_salt(d,self.salt_band)

                dist = gaussian_kde(salted)
                while len(smp)<self.K:
                    smp += [x for x in dist.resample(self.K)[0] if x >= lim[0] and x <= lim[1]]
                #print self.q1theta[n].shape, array(smp[:self.K]).shape
                self.q1theta[n] = array(smp[:self.K])
                self.theta_dists[n] = Proposal(copy.deepcopy(n),copy.deepcopy(dist))

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
            if i%100 == 0 and self.verbose:
                print "==> L = %s\r"%i

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

    def abcRun(self,fitfun=None, data={}, t=1,pool=False,savetemp=False):
        """
        Runs the model for inference through Approximate Bayes Computation
        techniques. This method should be used as an alternative to the sir.
        
        :Parameters:
             - `fitfun`: Callable which will return the goodness of fit of the model to data as a number between 0-1, with 1 meaning perfect fit
             - `t`: number of time steps to retain at the end of the of the model run for fitting purposes.
             - `data`: dict containing observed time series (lists of length t) of the state variables. This dict must have as many items the number of state variables, with labels matching variables names. Unorbserved variables must have an empty list as value.
             - `pool`: if True, Pools the user provided priors on the model's outputs, with the model induced priors.
             - `savetemp`: Should temp results be saved. Useful for long runs. Alows for resuming the simulation from last sa
        """
        seed()
        if not fitfun:
            fitfun = basicfit
        if savetemp:
            CP.dump(self.q1theta,open('q1theta','w'))
#       Running the model ==========================
        phi = self.runModel(savetemp,t)

        print "==> Done Running the K replicates\n"
        # Do Log Pooling
        if not pool:
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
        print "Calculating weights"
        po = Pool()
        jobs = [po.apply_async(fitfun, (phi[i],data)) for i in xrange(phi.shape[0])]
        w = [j.get() for j in jobs]
        po.close();po.join()
        w /=sum(w)
        w = 1-w
        
        w = nan_to_num(w)
        w = array(w)*qtilphi
        w /=sum(w)
        w = nan_to_num(w)
        print 'max(w): %s\nmean(w): %s\nvar(w): %s'%(max(w), mean(w), var(w))
        if sum(w) == 0.0:
            print 'Resampling weights are all zero, please check your model or data.'
            return 0
        print "Resampling Thetas"
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

    def imp_sample(self,n,data, w):
        """
        Importance sampling
        
        :Returns:
            returns a sample of size n
        """
        #sanitizing weights
        print "Starting importance Sampling"
        w /=sum(w)
        w = nan_to_num(w)
        j=0
        k=0
        smp = copy.deepcopy(data[:n])
        while j < n:
            i = randint(0,w.size)# Random position of w
            if random() <= w[i]:
                smp[j] = data[j]
                j += 1
                
            k+=1
        print "Done imp samp."
        return smp
    
    def mcmc_run(self, data, t=1, likvariance=10,burnin=1000, nopool=False, method="MH" ):
        """
        MCMC based fitting

        :Parameters:
            - `data`: observed time series on the model's output
            - `t`: length of the observed time series
            - `likvariance`: variance of the Normal likelihood function
            - `nopool`: True if no priors on the outputs are available. Leads to faster calculations
            - `method`: Step method. defaults to Metropolis hastings
        """
        #self.phi = recarray((self.K,t),formats=['f8']*self.nphi, names = self.phi.dtype.names)
        ta = True #if self.verbose else False
        tc = True #if self.verbose else False
        
        if method == "MH":
            sampler = MCMC.Metropolis(self, self.K,self.K*10, data, t, self.theta_dists, self.q1theta.dtype.names, self.tlimits, like.Normal, likvariance, burnin, trace_acceptance=ta,  trace_convergence=tc)
            sampler.step()
            self.phi = sampler.phi
            #self.mh(self.K,t,data,like.Normal,likvariance,burnin)
        else:
            sys.exit("Invalid MCMC method!\nTry 'MH'.")
        self.done_running = 1
        return 1

    def _output_loglike(self, prop, data, likfun=like.Normal,likvar=1e-1, po=None):
        """
        Returns the log-likelihood of a simulated series
        
        :Parameters:
            - `prop`: Proposed output
            - `data`: Data against which proposal will be measured
            - `likfun`: Likelihood function
            - `likvar`: Variance of the likelihood function
            - `po`: Pool of processes for parallel execution
        
        :Types:
            - `prop`: array of shape (t,nphi) with series as columns.
            - `data`: Dictionary with keys being the names (as in phinames) of observed variables
            - `likfun`: Log likelihood function object
        """
        if isinstance(prop, numpy.recarray):
            prop= numpy.array(prop.tolist())
        t = prop.shape[0] #1 if model's output is a scalar, larger if it is a time series (or a set of them)
        lik=0
        for k in xrange(self.nphi): #loop on series
            if self.q2phi.dtype.names[k] not in data:
                continue#Only calculate liks of series for which we have data
            obs = data[self.q2phi.dtype.names[k]]
            if po != None:# Parallel version
                lik = [po.apply_async(likfun,(obs[p],prop[p][k],1./likvar)) for p in range(t)]
                lik = sum([l.get() for l in lik])
            else:
                for p in xrange(t): #Loop on time
                    lik += likfun(obs[p],prop[p][k],1./likvar)
        return lik
    def sir(self, data={}, t=1,variance=0.1, pool=False,savetemp=False):
        """
        Run the model output through the Sampling-Importance-Resampling algorithm.
        Returns 1 if successful or 0 if not.

        :Parameters:
            - `data`: observed time series on the model's output
            - `t`: length of the observed time series
            - `variance`: variance of the Normal likelihood function
            - `pool`: False if no priors on the outputs are available. Leads to faster calculations
            - `savetemp`: Boolean. create a temp file?
        """
        seed()
        phi = self.runModel(savetemp,t)
        # Do Log Pooling
        if not pool:
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

#       Calculating the likelihood of each phi[i] considering the observed data
        lik = zeros(self.K)
        t0=time()
        po = Pool()
        for i in xrange(self.K):
            l=1
            for n in data.keys():
                if isinstance(data[n],list) and data[n] == []: 
                    continue #no observations for this variable
                elif isinstance(data[n],numpy.ndarray) and (not data[n].any()):
                    continue #no observations for this variable
                p = phi[n]
                liklist=[po.apply_async(like.Normal,(data[n][m], j, 1./variance)) for m,j in enumerate(p[i])]
                l=sum([p.get() for p in liklist])
                #l *= product([exp(like.Normal(data[n][m], j,1./2*j)) for m,j in enumerate(p[i])])
                #l += sum([like.Normal(data[n][m], j,1./(tau*j+.0001)) for m,j in enumerate(p[i])])
            lik[i]=l
        po.close()
        po.join()
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
            print '==> RMS deviation of outputs: %s'%(basicfit(phi, data),)
            return 0
        return 1
    def model_as_ra(self, theta):
        """
        Does a single run of self.model and returns the results as a record array
        """
        r = self.model(*theta)
        res = recarray(r.shape[0],formats=['f8']*self.nphi, names = self.phi.dtype.names)
        for i, n in enumerate(res.dtype.names):
            res[n] = r[:, i]
        return res
        
    def runModel(self,savetemp,t=1, k=None):
        '''
        Handles running the model k times keeping a temporary savefile for
        resuming calculation in case of interruption.

        :Parameters:
            - `savetemp`: Boolean. create a temp file?
            - `t`: number of time steps
        
        :Returns:
            - self.phi: a record array of shape (k,t) with the results.
        '''
        if savetemp:
            CP.dump(self.q1theta,open('q1theta','w'))
        if not k:
            k = self.K
#       Running the model ==========================
        
                
        if os.path.exists('phi.temp'):
            self.phi,j = CP.load(open('phi.temp','r'))
        else:
            j=0
            self.phi = recarray((k,t),formats=['f8']*self.nphi, names = self.phi.dtype.names)
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
        for i in xrange(j,k):
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
        print "==> Done Running the K (%s) replicates (took %s seconds)\n"%(k,(time()-t0))
        
        return self.phi

def basicfit(s1,s2):
    '''
    Calculates a basic fitness calculation between a model-
    generated time series and a observed time series.
    it uses a Mean square error.

    :Parameters:
        - `s1`: model-generated time series. record array.
        - `s2`: observed time series. dictionary with keys matching names of s1

    :Return:
        Root mean square deviation between ´s1´ and ´s2´.
    '''
    mse = []
    for k in s2.keys():
        if s2[k] == [] or (not s2[k].any()):
            continue #no observations for this variable
        e = mean((s1[k]-s2[k])**2.)
        mse.append(e) #min to guarantee error is bounded to (0,1)
    #print mean(mse),  
    return mean(mse) #mean r-squared
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
        P.subplot(floor(sqrt(nv)),floor(sqrt(nv))+1,i+1)
        P.hist(arr[n],bins=50, normed=1, label=n)
        P.legend()


def main2():
    start = time()
    #Me = Meld(K=5000,L=1000,model=model, ntheta=2,nphi=1,verbose=False,viz=False)
    Me.setTheta(['r','p0'],[stats.uniform,stats.uniform],[(2,4),(0,5)], [(0, 10), (0, 10)])
    Me.setPhi(['p'],[stats.uniform],[(6,9)],[(0,10)])
    #Me.add_data(normal(7.5,1,400),'normal',(6,9))
    #Me.run()
    Me.sir(data ={'p':[7.5]} )
    pt,pp = Me.getPosteriors(1)
    end = time()
    print end-start, ' seconds'
    plotRaHist(pt)
    plotRaHist(pp)
    P.show()
    
    
def mh_test():
    start = time()
    #Me = Meld(K=5000,L=1000,model=model, ntheta=2,nphi=1,verbose=False,viz=False)
    Me.setTheta(['r','p0'],[stats.uniform,stats.uniform],[(2,4),(0,5)], [(0, 10), (0, 10)])
    Me.setPhi(['p'],[stats.uniform],[(6,9)],[(0,10)])
    Me.mcmc_run(data ={'p':[7.5]},burnin=1000)
    pt,pp = Me.getPosteriors(1)
    end = time()
    print end-start, ' seconds'
    plotRaHist(pt)
    plotRaHist(pp)
    P.show()
    

if __name__ == '__main__':
    Me = Meld(K=5000,L=1000,model=model, ntheta=2,nphi=1,verbose=True,viz=False)
    mh_test()
    #main2()
     

