#-----------------------------------------------------------------------------
# Name:        Melding.py
# Purpose:     Bayesian melding
#
# Author:      Flávio Codeço Coelho
#
# Created:     2003/06/10
# RCS-ID:      $Id: Melding.py $
# Copyright:   (c) 2003
# Licence:     GPL
# New field:   Whatever
#-----------------------------------------------------------------------------
from Numeric import *
from RandomArray import *
from math import *
#from matplotlib.matlab import *

def Pooling(priors):
    """
    Pooling(priors)
    Returns the logarithmic pooling of priors.
    priors is a list of one dimensional arrays (distributions)
    """
    l = len(priors) # number of priors to pool
    alfa = 1.0/float(l) # geometric pooling
    print(alfa)
    pw=[0]*l # initializing a list with l elements
    for i in range(l):
        pw[i] = priors[i]**alfa #weighting
    p = product(pw)
    p2 = p/sum(p) #renormalization
    return p2

def invMod(q1,q1est,qtilphi):
    """
    invMod(q1,q1est,qtilphi)
    calculates and returns qtilteta from the three argumens above.
    """
    l = len(q1est)
    L = len(q1)
    qtilteta = zeros(L, Float)
    for i in range(l):
        qtilteta[i] = qtilphi[i]*(q1[i]/q1est[i]) # Equation 13 on Poole & Raftery, 1998
    
    qtilteta[L-1] = 1-sum(qtilteta)
    return qtilteta

if __name__ == '__main__':
    q1 = array([0.7,0.2, 0.1])
    q2 = array([0.6,0.4])
    q1est = array([.7,.3])
    qtilphi=Pooling([q2,q1est])
    print ['qtilphi = ',qtilphi]
    qtilteta=invMod(q1,q1est,qtilphi)
    print (qtilteta)
    pass # add a call to run your script here
