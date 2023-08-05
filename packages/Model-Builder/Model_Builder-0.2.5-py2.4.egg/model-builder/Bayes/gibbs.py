# -*- coding:iso8859-1 -*-
#-----------------------------------------------------------------------------
# Name:        gibbs.py
# Purpose:     This simple routine implements a simple Gibbs sampler.
#
# Author:      Flávio Codeço Coelho
#
# Created:     2003/25/09
# RCS-ID:      $Id: module1.py $
# Copyright:   (c) 2003
# Licence:     GPL
# Acknowledgements:   Whatever
#-----------------------------------------------------------------------------

from math import *
from RandomArray import *
from matplotlib.pylab import * 


n=10000
rho=.99 #correlation
#Means
m1 = 10
m2 = 20
#Standar deviations
s1 = 1
s2 = 1
#Initialize vectors
x=zeros(n, Float)
y=zeros(n, Float)
sd=sqrt(1-rho**2)
# the core of the method: sample recursively from two normal distributions
# Tthe mean for the current sample, is updated at each step.
for i in range(1,n):
  x[i] = normal(m1+rho*(y[i-1]-m2)/s2,s1*sd)
  y[i] = normal(m2+rho*(x[i-1]-m1)/s1,s2*sd)

scatter(x,y,marker='d',c='r')
title('Amostrador de Gibbs')
xlabel('x')
ylabel('y')
grid()

show()
