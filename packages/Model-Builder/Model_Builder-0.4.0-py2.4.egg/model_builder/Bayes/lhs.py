#-----------------------------------------------------------------------------
# Name:        lhs.py
# Purpose:     Implements the Latin Hypercube Sampling technique as described by
#              Iman and Conover, 1982, including correlation control both for no 
#              correlation or for a specified correlation matrix for the sampled 
#              parameters.
#
# Author:      Antonio Guilherme Pacheco, Flavio Codeco Coelho
#
# Created:     2006/08/27
# RCS-ID:      $Id: lhs.py $
# Copyright:   (c) 2004
# Licence:     gpl
# New field:   Whatever
#-----------------------------------------------------------------------------
#!/usr/bin/python
"""
Implements the Latin Hypercube Sampling technique as described
by Iman and Conover, 1982, including correlation control
both for no correlation or for a specified correlation matrix 
for the sampled parameters
"""
from pylab import plot, figure,hist,show
#import random
import scipy.stats as stats
import numpy
from numpy.linalg import cholesky,inv

#import psyco
#psyco.full()
valid_dists = ['Normal','Triangular','Uniform']
def rank_restr(nparms=4, Iter=100, noCorrRestr=True, matCorr=None):
    """
    Does the correlation control.
    """
    x=[numpy.arange(1,Iter+1)for i in xrange(nparms)]
    if noCorrRestr:
        
        for i in xrange(nparms):
            numpy.random.shuffle(x[i])
            #x.append(numpy.array(random.sample(xrange(1,Iter+1), Iter)))
        return x
    else:
        if matCorr==None:
            C=numpy.core.numeric.identity(nparms)
        else:
            C=numpy.matrix(matCorr)
        s0=numpy.arange(1.,Iter+1)/(Iter+1.)
        s=stats.norm().ppf(s0)
        s1=[]
        for i in xrange(nparms):
            numpy.random.shuffle(s)
            s1.append(s.copy())
        S=numpy.matrix(s1)
        #print S,S.shape
        E=numpy.corrcoef(S)
        P=cholesky(C)
        Q=cholesky(E)
        Final=S.transpose()*inv(Q).transpose()*P.transpose()
        for i in xrange(nparms):
            x.append(stats.stats.rankdata(Final.transpose()[i,]))
        return x

def sample_cum(Iter=100):
    """
    Calculates samples on the quantile axis
    One sample per quantile
    """
    perc = numpy.arange(0,1,1./Iter)
    smp = [stats.uniform(i,1./Iter).rvs()[0] for i in perc]
    return smp



def sample_dist(cum, dist='Normal', parms=[0,1]):
    """
    Return a sample from from the given distribution 
    by inverting the cumulative prob. density function
    """
    if dist == 'Normal':
        if len(parms) == 2:
            n = stats.norm(parms[0],1./parms[1])
            d = n.ppf(cum)
    elif dist=='Triangular':
        if len(parms) ==3 and parms[0]<=parms[1]<=parms[2]:
            loc=parms[0]
            scale=parms[2]-parms[0]
            t = stats.triang((float(parms[1])-loc)/scale,loc=loc,scale=scale)
            d = t.ppf(cum)
    elif dist == 'Uniform':
        loc = parms[0]
        scale = parms[1]-parms[0]
        d = stats.uniform(loc,scale).ppf(cum)
    else:
        print '%s is an unsupported distribution!'%dist
        
    return d



def lhs(Pars, dists, parms, Iter=100, noCorrRestr=True, matCorr=None):
    """
    Returns tuple of vectors
    Pars: list of strings with parameter names
    dists: List of strings with distribution names
    Iter: sample size
    defaults to no correlation between sampled parameters
    """
    ParsList=[]
    if len(Pars)==len(dists):
        indexes=rank_restr(nparms=len(dists), Iter=Iter, noCorrRestr=noCorrRestr, matCorr=matCorr)
        for i in xrange(len(dists)):
            v=sample_dist(sample_cum(Iter), dist=dists[i], parms=parms[i])
            index=map(int,indexes[i]-1)
            ParsList.append(v[index])
    return ParsList
            
    

if __name__=='__main__':
    #c=lhs(['Par1', 'Par2', 'Par3'],['Normal','Triangular','Uniform'], [[0,1], [1,5,8], [1,2]],100000)
    c=lhs(['Par1', 'Par2', 'Par3'],['Normal','Triangular','Uniform'], [[0,1], [1,5,8], [1,2]],10000, noCorrRestr=True)
  #  m=[[1,.3595,-.2822],[.3595,1,-.1024],[-.2822,-.1024,1]]
  #  c=lhs(['Par1', 'Par2', 'Par3'],['Normal','Triangular','Uniform'], [[0,1], [1,5,8], [1,2]],100000, noCorrRestr=False, matCorr=m)
    print stats.spearmanr(c[0],c[1])
    print stats.spearmanr(c[0],c[2])
    print stats.spearmanr(c[1],c[2])
    
##    print c
##    print 'done!'
    #a=sample_cum(10000)
    #b=sample_dist(a, dist='Triangular', parms=[1,5,8])
    
    #plot(b,a, 'bo')
##    print c[0].shape,c[1].shape,c[2].shape
##    print c[0][0], type(c[0][0])
    hist(c[0], bins=30)
    figure()
    hist(c[1], bins=30)
    figure()
    hist(c[2], bins=30)
    show()
    
