# -*- coding:iso8859-1 -*-
#-----------------------------------------------------------------------------
# Name:        rejectBayes.py
# Purpose:     The Bayes theorem by the rejection sampling algorithm.
#
# Author:      Flávio Codeço Coelho (fccoelho@cienciaaberta.org>
#
# Created:     2003/26/09
# RCS-ID:      $Id: rejection.py $
# Copyright:   (c) 2003
# Licence:     GPL
#-----------------------------------------------------------------------------
from math import *
from RandomArray import *
from matplotlib.pylab import *

def Likeli(data, limits, nl):
    """
    Generates the likelihood function of data assuming 
    a normal distribution.
    limits is a tuple setting the interval 
    be used as the support for the Likelihood function.
    returns a vector.
    """
    n = len(data) # Number of data points
    data = array(data)
    (ll,ul) = limits #limits for the parameter space
    step = (ul-ll)/float(nl)
    res = [] #empty list of results
    sd = std(data) #standard deviation of data
    for mu in arange(ll,ul,step):
        res.append(exp(-0.5*sum(((data-mu)/sd)**2))) 
        
    lik = array(res)/max(array(res)) # Likelihood function   
    return lik

def sampler(n, data):
    """
    This function samples from x and 
    returns a vector shorter that len(vector size)
    """
    x=uniform(0,1,n) #support
    limits = 0,1
    L=Likeli(data, limits, n)
    fx=6*x*(1-x) # prior, f(x) is a beta(2,2) PDF
    #return only those x values that satisfy the condition
    s=compress(L[:len(x)]<fx,x) 
    scatter(x,fx)
    #print len(L), len(x)
    #plot(sort(x),L)
    legend('Prior')
    return s

def efficiency(vector,n, data):
    """
    tests the efficiency of the sampling procedure.
    """
    l = len(vector)
    prob = l/float(n)
    diff = n-l
    n2 = int(diff/prob) #n required to obtain the remaining samples needed
    vec2 = sampler(n2,data)
    s = concatenate((vector,vec2))
    return s,prob

def main():
    n=90000
    data = uniform(0,1,59) #3 data points
    sample=sampler(n, data)
    s,prob = efficiency(sample,n, data)
    #generates histogram
    figure(2)
    hist(s, bins=50,normed=1)
    xlabel('x')
    text(0.8,1.2,'Efficiency:%s'%round(prob,2))
    ylabel('frequency')
    title('Posterior: n=%s'% n)
    show()
    return s
    
if __name__ == '__main__':
    main() 
