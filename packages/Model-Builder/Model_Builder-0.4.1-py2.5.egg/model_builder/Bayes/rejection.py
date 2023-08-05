# -*- coding:iso8859-1 -*-
#-----------------------------------------------------------------------------
# Name:        rejection.py
# Purpose:     The rejection sampling algorithm.
#
# Author:      Flávio Codeço Coelho (fccoelho@fiocruz.br>
#
# Created:     2003/26/09
# RCS-ID:      $Id: rejection.py $
# Copyright:   (c) 2003,2004,2005
# Licence:     GPL
#-----------------------------------------------------------------------------
from math import *
from RandomArray import *
from matplotlib.pylab import *

def sampler(n):
    """
    This function samples from x and returns a vetor shorter that len(vector size)
    """
    x=uniform(0,1,n) #Sample
    y=uniform(0,1,n)*1.5 #Envelope
    fx=6*x*(1-x) # Target. x has a beta distribution
    s=compress(y<fx,x) #return only those values that satisfy the condition
    return s

def efficiency(vector,n):
    """
    tests the efficiency of the sampling procedure.
    returns acceptance probability
    """
    l = len(vector)
    prob = l/float(n)
    diff = n-l
    n2 = int(diff/prob) #n required to obtain the remaining samples needed
    vec2 = sampler(n2)
    s = concatenate((vector,vec2))
    #generates histogram
    nb, bins, patches = hist(s, bins=50, normed=0)
    

    xlabel('s')
    ylabel('frequency')
    title('Histogram of s: n=%s'% n)
    show()
    return s
    

def testRS():
    """
    this function tests the module
    """
    n=100000
    sample=sampler(n)
    efficiency(sample,n)
    
    
if __name__ == '__main__':
    testRS() # if this program is ran by itself it will test the algorithm and return its efficiency
