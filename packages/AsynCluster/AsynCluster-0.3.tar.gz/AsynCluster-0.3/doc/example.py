#!/usr/bin/env python
#
# AsynCluster:
# A cluster management server based on Twisted's Perspective Broker. Dispatches
# cluster jobs and regulates when and how much each user can use his account on
# any of the cluster node workstations.
#
# Copyright (C) 2006-2007 by Edwin A. Suominen, http://www.eepatents.com
#
# This program is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free Software
# Foundation; either version 2 of the License, or (at your option) any later
# version.
# 
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the file COPYING for more details.
# 
# You should have received a copy of the GNU General Public License along with
# this program; if not, write to the Free Software Foundation, Inc., 51
# Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA

"""
This script shows how Bayesian inference can be run on a cluster of nodes to
identify the location (median) and scale (half-width at half-maximum) of a
Cauchy-distributed random process.
"""

import time, os.path
from random import sample as sampleWOR

import scipy as s
from scipy import stats

from twisted.internet import defer, reactor, threads

from asynqueue import ThreadQueue
from asyncluster.master import jobs
from twisted_goodies.pybywire import pack


def sample(W, N=None, logWeights=False):
    """
    Returns an index array that samples I{N} values from some external
    array. Each element of the array will have a probability of being
    sampled (with replacement) that is proportional to its corresponding
    weight in the 1-D array I{W}.

    Uses Walker's alias algorithm as set forth in L. Devroye, Non-Uniform
    Random Variate Generation, p. 109,
    http://cg.scs.carleton.ca/~luc/rnbookindex.html.

    If N is not specified, it defaults to the length of W, i.e., importance
    resampling.

    If I{logWeights} is set C{True}, the weights are transformed from log
    to linear.
    """
    if logWeights:
        W = s.exp(W - W.max())
    W /= sum(W)
    I0 = (s.isfinite(W) * s.greater(W, 1E-7)).nonzero()[0]
    K = len(W[I0])
    if N is None:
        N = K
    if K == 0:
        return []
    if K == 1:
        return [0]*N            
    greater, smaller = [], []
    T = s.zeros((K,2))
    for m, w in enumerate(W[I0]):
        q = T[m,0] = K*w
        if q < 1:
            smaller.append(m)
        else:
            greater.append(m)
    while smaller and greater:
        k = greater[-1]
        m = smaller.pop()
        T[m,1] = k
        T[k,0] -= (1 - T[m,0])
        if T[k,0] < 1:
            greater.pop()
            smaller.append(k)
    V = s.rand(N)
    RI = s.random.randint(0, K-1, N)
    I1 = s.greater(V, T[RI,0]).choose(RI, T[RI,1].astype(int))
    return I0[I1]


class Proposer(object):
    """
    I provide random variates and probabilities for jumps to be made in
    proposing each new parameter vector. The jumps have a normal (Gaussian)
    distribution, as is typical. It doesn't matter that we're trying to model a
    somewhat different distribution.
    """
    def __init__(self):
        self._jumpDist = stats.distributions.norm()
    
    def r(self, N, wiggle):
        """
        Returns an array of I{N} rows of parameter offsets drawn from the prior
        distributions scaled by a I{wiggle} value between 0 and 1.
        """
        return wiggle * self._jumpDist.rvs((N, 2))

    def p(self, X, wiggle):
        """
        Returns a vector of probability densities for each parameter offset in
        X, or rows of X, under the assumption that they were generated from my
        L{rProposal} method with the specified I{wiggle}.
        """
        if len(X.shape) == 1:
            X = X.reshape(1, X.shape[0])
        N = X.shape[0]
        return self._jumpDist.pdf(X/wiggle) / wiggle


class NodeCaller(object):
    """
    I call on nodes to compute likelihoods of data given vectors of parameters.
    """
    nodecode = """
    ###########################################################################
    import scipy as s
    from scipy import stats
    from twisted_goodies.pybywire import pack

    G = {}

    def newData(data):
        G['data'] = pack.Unpacker(data)()

    def likelihood(paramVector):
        X = pack.Unpacker(paramVector)()
        # The next two lines are where all the real computing work gets done
        distObj = stats.distributions.cauchy(loc=X[0], scale=X[1])
        L = s.log(distObj.pdf(G['data'])).sum()
        return pack.Packer(L)()
    
    ###########################################################################
    """
    def __init__(self, socket, data):
        self.socket, self.data = socket, data
    
    def _oops(self, failure):
        print "FAILURE:\n%s" % failure.getTraceback()

    def startup(self):
        """
        Starts me up to run the named model remotely on the asyncluster nodes
        via the supplied UNIX domain I{socket}. Returns a deferred that fires
        when remotely-run operations can commence.
        """
        def maybeStarted(status):
            if not status:
                raise Exception("Client couldn't connect!")
            reactor.addSystemEventTrigger(
                'before', 'shutdown',  self.client.shutdown)
            d = self.client.update('newData', pack.Packer(self.data)())
            d.addErrback(self._oops)
            return d
        
        self.client = jobs.JobClient(self.socket, codeString=self.nodecode)
        return self.client.startup().addCallback(maybeStarted)
    
    def likelihood(self, X, runLocally=False):
        """
        Returns the log-likelihood of my data given the Cauchy distribution of
        my model, after application of the location and scale parameters from
        the supplied 2-element parameter vector I{X}.

        This method returns the likelihood of the data given the parameters. It
        does not consider any prior probability of the parameters; in this
        example a 'non-informative uniform prior' is used.
        """
        def localLikelihood():
            distObj = stats.distributions.cauchy(loc=X[0], scale=X[1])
            return s.log(distObj.pdf(self.data)).sum()
        
        def gotResult(L_packed):
            return pack.Unpacker(L_packed)()

        if runLocally:
            d = threads.deferToThread(localLikelihood)
        else:
            X_packed = pack.Packer(X)()
            d = self.client.run('likelihood', X_packed, **{'timeout':20})
            d.addCallbacks(gotResult, self._oops)
        return d


class Population_Monte_Carlo(object):
    """
    Population MCMC with per Cappe et al.

    I fit the location (median and mode) and scale (half-width at half-maximum)
    of a Cauchy distribution to a set of observations from a Cauchy random
    process. Basically, the Cauchy distribution accounts better for rare,
    significant events that would be vanishingly unlikely under a Gaussian
    model.

    This example could fit a normal distribution to Gaussian-distributed data
    instead, but that would be boring. You'd just be computing the mean and
    variance of the data set.
    """
    runLocally = False
    socket="/tmp/.ndm"
    V = [0.10, 0.02, 0.005, 0.001]

    def __init__(self, data):
        self.proposer = Proposer()
        self.caller = NodeCaller(self.socket, data)
        self.fh = open('params.csv', 'w')
        self.fh.write("loc, scale\n")

    def subsetIndex(self, k):
        """
        Returns a subset index for the samples in my I{X} attribute that
        correspond to the jump variance for the supplied index I{k}.
        """
        I = sampleWOR(self.Is, self.R[k])
        self.Is = s.setdiff1d(self.Is, I)
        return I

    def weightedProposals(self, X, v):
        """
        Returns a deferred that fires with a 1-D array of valid proposals on
        the supplied parameter array I{X}, given the specified proposal
        variance I{v}, along with log-importance weights for those proposals.

        Valid proposals are those with non-zero likelihood. The censoring to
        only valid proposals means that fewer proposals may be returned than
        supplied parameters, possibly no proposals at all.
        
        The importance weights are to be combined with those from other calls
        to this method with different variance settings. The weights will be
        used to resample the returned proposals so that the probability of any
        given proposal being included in the final result for this iteration is
        proportional to its likelihood, and inversely proportional to the
        probability density of the proposal offest.
        """
        def gotLikelihoods(results):
            XP = X + XD
            L = s.array(results)
            if len(L):
                I = s.isfinite(L).nonzero()[0]
                logProbJumps = s.log(self.proposer.p(XD[I], v)).sum(1)
                return XP[I], L[I] + logProbJumps
            return XP, L

        # Have the nodes evaluate the likelihood of each proposal, which is
        # the most time-consuming step in real-life usage.
        XD = self.proposer.r(len(X), v)
        dList = [self.caller.likelihood(Xp, self.runLocally) for Xp in X+XD]
        d = defer.gatherResults(dList)
        d.addCallback(gotLikelihoods)
        return d
    
    @defer.deferredGenerator
    def run(self, N_iter, N_chains):
        """
        Does a PMC run with I{N_chains} population members and jump variances
        in the supplied 1-D array I{V}. The number of population members for
        each jump variance will go up or down, depending on the performance for
        that setting.

        B{NOTE}: What I've been calling variances are actually computed as
        standard deviations, i.e., not squared. Should fix this either by
        relabeling or adjusting the code.
        
        Returns a deferred that fires when the run is done. No output value is
        provided via the deferred, however.

        @param N_iter: The number of iterations to produce after burn-in.

        @param N_chains: The number of Monte Carlo chains run at each
          iteration.
        
        """
        def gotWeightedProposals(results, k):
            XP[k] = results[0]
            W[k] = results[1]

        def normalize(R):
            # Rescale so that the proportions are global rather than
            # individual. Highly successful settings will have a large portion
            # of the next sample even if they last operated on only a few of
            # the samples.
            R = R.astype(float) / R.sum()
            # Turn the scaled array into an array of subsample sizes, with a
            # minimum size of two apiece.
            R = s.clip(
                s.round_(N_chains*R), rMin,
                N_chains-rMin*(P-1)).astype(int)
            # Twiddle the biggest one as needed to keep sum = N_chains
            R[s.argmax(R)] += N_chains - sum(R)
            # Replace the old list and subset index
            self.R = R
            self.Is = s.arange(N_chains)

        # Connect the node caller to the AsynCluster master server
        wfd = defer.waitForDeferred(self.caller.startup())
        yield wfd; wfd.getResult()
        # Some constants
        P = len(self.V)
        rMin = max([2, int(round(0.01*N_chains))])
        # Initialize some arrays
        normalize(s.ones(P))
        X = self.proposer.r(N_chains, self.V[0])
        # The iteration loop
        for i in xrange(N_iter):
            t0 = time.time()
            # Generate and weight some proposals
            XP, W, II = [[None]*P for k in (1,2,3)]
            dList = []
            for k, v in enumerate(self.V):
                I = II[k] = self.subsetIndex(k)
                d = self.weightedProposals(X[I], v)
                d.addCallback(gotWeightedProposals, k)
                dList.append(d)
            wfd = defer.waitForDeferred(defer.DeferredList(dList))
            yield wfd; wfd.getResult()
            # Resample everything together
            I = sample(s.concatenate(W), N_chains, logWeights=True)
            if len(I):
                X = s.row_stack(XP)[I]
            R = s.array([sum([x in II[k] for x in I]) for k in xrange(P)])
            # Write the parameters for this iteration to the output file
            for Xk in X:
                rowString = ", ".join(["%f" % x for x in Xk])
                self.fh.write(rowString + "\n")
            # Normalize R to maintain a total of N_chains population members
            normalize(R)
            # Provide some info about this iteration
            vInfo = ", ".join(["%3d" % r for r in self.R])
            msg = "%04d, %5.2f sec, VR={%s} :  %s" % (
                i, time.time()-t0, vInfo,
                ", ".join(["%9.3g" % x for x in X.mean(0)]))
            print msg
        # All done
        self.fh.close()
        reactor.stop()


if __name__ == '__main__':
    # Parameters for the example
    N_obs = 50000
    N_chains = 1000
    N_iter = 1000
    loc, scale = 0.1, 0.4

    # Create some fake observations of a Cauchy random process
    distObj = stats.distributions.cauchy(loc=loc, scale=scale)
    data = distObj.rvs(N_obs)
    fh = open('data.csv', 'w')
    for x in data:
        fh.write("%f\n" % x)
    fh.close()
    
    # Create the Monte Carlo runner and set up the run
    pmc = Population_Monte_Carlo(data)
    reactor.callWhenRunning(pmc.run, N_iter, N_chains)

    # Run!
    reactor.run()
